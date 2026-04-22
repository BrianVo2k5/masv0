"""
training.py — BART-large LoRA fine-tune on XSUM
Reads all settings from train_config.yaml

Checkpoint strategy:
  - Every `save_steps` steps → kept natively by Hugging Face Trainer.
  - End of training          → final/

Usage:
    python training.py                        # uses train_config.yaml next to this file
    python training.py --config my_cfg.yaml   # override config path
"""

import argparse
import logging
from pathlib import Path

import torch
import yaml
from datasets import load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    BartForConditionalGeneration,
    BartTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    set_seed,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Config loader
# ══════════════════════════════════════════════════════════════════════════════

def load_config(path: str) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    log.info(f"Loaded config from {path}")
    return cfg


# ══════════════════════════════════════════════════════════════════════════════
# Dataset preprocessing
# ══════════════════════════════════════════════════════════════════════════════

def preprocess_factory(tokenizer, cfg: dict):
    max_in  = cfg["dataset"]["max_input_len"]
    max_out = cfg["dataset"]["max_target_len"]

    # Read column names from config, fallback to XSUM defaults just in case
    text_col = cfg["dataset"].get("text_column", "document")
    sum_col  = cfg["dataset"].get("summary_column", "summary")

    def preprocess(batch):
        inputs = tokenizer(
            batch[text_col],
            max_length=max_in,
            truncation=True,
            padding=False,          # DataCollator handles padding per-batch
        )
        targets = tokenizer(
            batch[sum_col],
            max_length=max_out,
            truncation=True,
            padding=False,
        )
        labels = [
            [(t if t != tokenizer.pad_token_id else -100) for t in seq]
            for seq in targets["input_ids"]
        ]
        inputs["labels"] = labels
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
    dtype_map = {"fp32": torch.float32, "fp16": torch.float16, "bfloat16": torch.bfloat16}
    dtype = dtype_map[cfg["model"]["torch_dtype"]]

    # ── Tokenizer & model ──────────────────────────────────────────────────
    model_id = cfg["model"]["model_id"]
    log.info(f"Loading tokenizer: {model_id}")
    tokenizer = BartTokenizer.from_pretrained(model_id)

    log.info(f"Loading model: {model_id} ({dtype})")
    model = BartForConditionalGeneration.from_pretrained(model_id, torch_dtype=dtype)

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
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # ── Dataset ────────────────────────────────────────────────────────────
    ds_cfg = cfg["dataset"]
    log.info("Loading XSUM …")
    raw = load_dataset(ds_cfg["name"], ds_cfg.get("version") or None)
    train_ds = raw[ds_cfg["train_split"]]
    val_ds   = raw[ds_cfg["val_split"]]

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
        bf16=t["bf16"],
        fp16=t["fp16"],
        dataloader_pin_memory=t["dataloader_pin_memory"],
        eval_strategy=t.get("eval_strategy", t.get("evaluation_strategy", "no")),
        
        # Native save configuration
        save_strategy="steps",
        save_steps=ck["save_steps"],
        save_total_limit=None,          # explicitly keep ALL checkpoints
        
        logging_steps=t["logging_steps"],
        predict_with_generate=False,    
        report_to="none",               
        seed=t["seed"],
    )

    # ── Trainer ────────────────────────────────────────────────────────────
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer, 
        data_collator=collator,
        # callbacks removed completely
    )

    log.info("Starting fresh training run …")
    trainer.train(resume_from_checkpoint=args.resume)

    # ── Final save ─────────────────────────────────────────────────────────
    final_dir = Path(t["output_dir"]) / "final"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    log.info(f"Training complete. Final model → {final_dir}")


if __name__ == "__main__":
    main()