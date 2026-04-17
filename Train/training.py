"""
training.py — BART-large LoRA fine-tune on CNN/DailyMail
Reads all settings from train_config.yaml

Checkpoint strategy:
  - Every `save_steps` steps → keep last `keep_last_n_steps` (rolling)
  - End of every epoch        → always kept (epoch-N/) when save_at_epoch_end is true
  - End of training           → final/

Usage:
    python training.py                        # uses train_config.yaml next to this file
    python training.py --config my_cfg.yaml   # override config path
    python training.py --resume ./runs/bart-lora/step-1000   # resume from checkpoint
"""

import argparse
import logging
import shutil
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
    TrainerCallback,
    TrainerControl,
    TrainerState,
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
# Rolling checkpoint callback
# Keeps last N step-checkpoints; epoch checkpoints are never deleted.
# ══════════════════════════════════════════════════════════════════════════════

class RollingCheckpointCallback(TrainerCallback):
    def __init__(self, output_dir: str, save_steps: int, keep_n: int, save_at_epoch_end: bool = True):
        self.output_dir = Path(output_dir)
        self.save_steps = save_steps
        self.keep_n = keep_n
        self.save_at_epoch_end = save_at_epoch_end
        self._step_checkpoints: list[Path] = []

    def on_save(self, args, state: TrainerState, control: TrainerControl, **kwargs):
        step = state.global_step
        ckpt_dir = self.output_dir / f"step-{step}"

        # Trainer saves to checkpoint-{step}; copy to our named scheme
        trainer_dir = self.output_dir / f"checkpoint-{step}"
        if trainer_dir.exists() and not ckpt_dir.exists():
            shutil.copytree(trainer_dir, ckpt_dir)
            log.info(f"Step checkpoint saved → {ckpt_dir}")

        self._step_checkpoints.append(ckpt_dir)

        # Prune oldest beyond keep_n
        while len(self._step_checkpoints) > self.keep_n:
            oldest = self._step_checkpoints.pop(0)
            if oldest.exists():
                shutil.rmtree(oldest)
                log.info(f"Removed old step checkpoint: {oldest}")

    def on_epoch_end(self, args, state: TrainerState, control: TrainerControl, **kwargs):
        if not self.save_at_epoch_end:
            return
        epoch = int(state.epoch)
        epoch_dir = self.output_dir / f"epoch-{epoch}"
        if self._step_checkpoints:
            src = self._step_checkpoints[-1]
            if src.exists() and not epoch_dir.exists():
                shutil.copytree(src, epoch_dir)
                log.info(f"Epoch checkpoint saved → {epoch_dir}")
        else:
            # Epoch ended before first save_steps hit — force a save
            control.should_save = True
            log.info(f"Epoch {epoch} ended before first step save — forcing save")


# ══════════════════════════════════════════════════════════════════════════════
# Dataset preprocessing
# ══════════════════════════════════════════════════════════════════════════════

def preprocess_factory(tokenizer, cfg: dict):
    max_in  = cfg["dataset"]["max_input_len"]
    max_out = cfg["dataset"]["max_target_len"]

    def preprocess(batch):
        inputs = tokenizer(
            batch["article"],
            max_length=max_in,
            truncation=True,
            padding=False,          # DataCollator handles padding per-batch
        )
        targets = tokenizer(
            text_target=batch["highlights"],
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
    log.info("Loading CNN/DailyMail …")
    raw = load_dataset(ds_cfg["name"], ds_cfg["version"])
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
        
        # Set max grad norm and dtype to fp32
        max_grad_norm=t.get("max_grad_norm", 1.0), 
        
        lr_scheduler_type=t["lr_scheduler_type"],
        
        # CHANGED: warmup_ratio replaced with warmup_steps
        warmup_steps=t.get("warmup_steps", 100), 
        
        weight_decay=t["weight_decay"],
        bf16=t["bf16"],
        fp16=t["fp16"],
        dataloader_pin_memory=t["dataloader_pin_memory"],
        
        # CHANGED: evaluation_strategy replaced with eval_strategy
        eval_strategy=t.get("eval_strategy", t.get("evaluation_strategy", "no")),
        
        save_strategy="steps",
        save_steps=ck["save_steps"],
        logging_steps=t["logging_steps"],
        predict_with_generate=False,    
        report_to="none",               
        seed=t["seed"],
    )

    rolling_cb = RollingCheckpointCallback(
        output_dir=t["output_dir"],
        save_steps=ck["save_steps"],
        keep_n=ck["keep_last_n_steps"],
        save_at_epoch_end=ck.get("save_at_epoch_end", True),
    )

    # ── Trainer ────────────────────────────────────────────────────────────
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        
        # CHANGED: tokenizer replaced with processing_class
        processing_class=tokenizer, 
        
        data_collator=collator,
        callbacks=[rolling_cb],
    )

    log.info("Starting training …")
    trainer.train(resume_from_checkpoint=args.resume)

    # ── Final save ─────────────────────────────────────────────────────────
    final_dir = Path(t["output_dir"]) / "final"
    trainer.save_model(str(final_dir))
    
    # We still explicitly save the tokenizer locally to ensure the vocabulary writes out correctly.
    tokenizer.save_pretrained(str(final_dir))
    log.info(f"Training complete. Final model → {final_dir}")


if __name__ == "__main__":
    main()