import argparse
import logging
from pathlib import Path

import numpy as np
import torch
import yaml
import evaluate as hf_evaluate
from datasets import load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    set_seed,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

rouge_metric = hf_evaluate.load("rouge")


# ══════════════════════════════════════════════════════════════════════════════
# Config loader
# ══════════════════════════════════════════════════════════════════════════════

def load_config(path: str) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    log.info(f"Loaded config from {path}")
    return cfg


# ══════════════════════════════════════════════════════════════════════════════
# ROUGE metrics 
# ══════════════════════════════════════════════════════════════════════════════

def make_compute_metrics(tokenizer):
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]

        # Trainer pads shorter generated sequences with a fill value that can exceed
        # vocab size. Clip to safe range first.
        preds = np.clip(preds, 0, tokenizer.vocab_size - 1).astype(np.int32)

        decoded_preds  = tokenizer.batch_decode(preds, skip_special_tokens=True)
        labels         = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        decoded_preds  = [p.strip() for p in decoded_preds]
        decoded_labels = [l.strip() for l in decoded_labels]

        result = rouge_metric.compute(
            predictions=decoded_preds,
            references=decoded_labels,
            use_stemmer=True,
        )
        return {k: round(v * 100, 2) for k, v in result.items()}

    return compute_metrics


# ══════════════════════════════════════════════════════════════════════════════
# Dataset preprocessing
# ══════════════════════════════════════════════════════════════════════════════

def preprocess_factory(tokenizer, cfg: dict):
    max_in   = cfg["dataset"]["max_input_len"]
    max_out  = cfg["dataset"]["max_target_len"]
    text_col = cfg["dataset"].get("text_column", "document")
    sum_col  = cfg["dataset"].get("summary_column", "summary")

    def preprocess(batch):
        # Collapse stray newlines
        documents = [" ".join(text.split()) for text in batch[text_col]]
        summaries = [" ".join(text.split()) for text in batch[sum_col]]

        inputs = tokenizer(
            documents,
            max_length=max_in,
            truncation=True,
            padding=False,          
        )
        targets = tokenizer(
            summaries,
            max_length=max_out,
            truncation=True,
            padding=False,
        )

        inputs["labels"] = [
            [(t if t != tokenizer.pad_token_id else -100) for t in seq]
            for seq in targets["input_ids"]
        ]
        return inputs

    return preprocess


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="train_config.yaml")
    parser.add_argument("--resume", default=None, help="Path to checkpoint dir to resume from")
    args = parser.parse_args()

    cfg = load_config(args.config)
    set_seed(cfg["training"]["seed"])

    # ── dtype ──────────────────────────────────────────────────────────────
    dtype_map = {
        "fp32": torch.float32, 
        "fp16": torch.float16, 
        "float16": torch.float16, 
        "bfloat16": torch.bfloat16
    }
    dtype = dtype_map[cfg["model"]["torch_dtype"]]

    # ── Tokenizer & model ──────────────────────────────────────────────────
    model_id = cfg["model"]["model_id"]
    log.info(f"Loading tokenizer: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    log.info(f"Loading model: {model_id} ({dtype})")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id, dtype=dtype)
    
    # Required when using gradient checkpointing
    model.config.use_cache = False 

    # ── LoRA ───────────────────────────────────────────────────────────────
    lora_cfg = cfg["lora"]
    peft_config = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["lora_alpha"],
        lora_dropout=lora_cfg["lora_dropout"],
        bias=lora_cfg["bias"],
        target_modules=lora_cfg["target_modules"],
    )
    model.enable_input_require_grads()
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # ── Dataset ────────────────────────────────────────────────────────────
    ds_cfg = cfg["dataset"]
    log.info(f"Loading {ds_cfg['name']} …")
    version = ds_cfg.get("version")
    raw = load_dataset(ds_cfg["name"], version) if version else load_dataset(ds_cfg["name"])
    train_ds = raw[ds_cfg["train_split"]]
    val_ds   = raw[ds_cfg["val_split"]]

    max_eval = ds_cfg.get("max_eval_samples")
    if max_eval and max_eval < len(val_ds):
        val_ds = val_ds.select(range(max_eval))
        log.info(f"Eval set capped at {max_eval} samples")

    preprocess = preprocess_factory(tokenizer, cfg)
    log.info("Tokenizing splits …")
    train_ds = train_ds.map(
        preprocess,
        batched=True,
        remove_columns=train_ds.column_names,
        num_proc=ds_cfg["num_workers"],
        desc="Tokenizing train",
    )
    val_ds = val_ds.map(
        preprocess,
        batched=True,
        remove_columns=val_ds.column_names,
        num_proc=ds_cfg["num_workers"],
        desc="Tokenizing val",
    )

    # ── Collator ────────────────────────────────────────────────────────────
    collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        label_pad_token_id=-100,
        pad_to_multiple_of=8,
    )

    # ── TrainingArguments ──────────────────────────────────────────────────
    t  = cfg["training"]
    ck = cfg["checkpointing"]

    training_args = Seq2SeqTrainingArguments(
        output_dir=t["output_dir"],
        num_train_epochs=t["num_train_epochs"],
        per_device_train_batch_size=t["per_device_train_batch_size"],
        gradient_accumulation_steps=t["gradient_accumulation_steps"],
        per_device_eval_batch_size=t["per_device_eval_batch_size"],
        learning_rate=float(t["learning_rate"]),
        max_grad_norm=t.get("max_grad_norm", 1.0),
        lr_scheduler_type=t["lr_scheduler_type"],
        warmup_steps=t.get("warmup_steps", 100),
        weight_decay=t["weight_decay"],
        label_smoothing_factor=t.get("label_smoothing_factor", 0.0),
        bf16=t["bf16"],
        fp16=t["fp16"],
        dataloader_pin_memory=t["dataloader_pin_memory"],
        dataloader_num_workers=t.get("dataloader_num_workers", 0),
        group_by_length=t.get("group_by_length", False),
        eval_strategy=t.get("eval_strategy", "no"),
        eval_accumulation_steps=t.get("eval_accumulation_steps"),
        predict_with_generate=t.get("predict_with_generate", False),
        generation_max_length=t.get("generation_max_length"),
        
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},

        save_strategy="steps",
        save_steps=ck["save_steps"],
        save_total_limit=ck.get("keep_last_n_steps", 3),

        logging_steps=t["logging_steps"],
        report_to="none",
        seed=t["seed"],
    )

    # ── Trainer ────────────────────────────────────────────────────────────
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer, # Note: if using older transformers (<4.45), change to tokenizer=tokenizer
        data_collator=collator,
        compute_metrics=make_compute_metrics(tokenizer),
    )

    log.info("Starting training …")
    trainer.train(resume_from_checkpoint=args.resume)

    # ── Final save ─────────────────────────────────────────────────────────
    final_dir = Path(t["output_dir"]) / "final"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    log.info(f"Training complete. Final model → {final_dir}")


if __name__ == "__main__":
    main()