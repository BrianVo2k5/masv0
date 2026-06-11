import argparse
import logging
from pathlib import Path

import torch
from peft import PeftConfig, PeftModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
log = logging.getLogger(__name__)

BASE_MODEL_ID = "facebook/bart-large"

DEFAULT_CHECKPOINT = Path(__file__).parent / "runs/bart-lora-xsum/checkpoint-7200"
DEFAULT_OUTPUT = Path(__file__).parent / "runs/models/model_bart-xsum.pt"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    checkpoint = Path(args.checkpoint)
    output = Path(args.output)

    if not checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")

    # Device + dtype
    if torch.cuda.is_available():
        dtype = torch.float16
    elif torch.backends.mps.is_available():
        dtype = torch.float16
    else:
        dtype = torch.float32

    log.info(f"Using dtype: {dtype}")

    # Load base model
    log.info("Loading base model...")
    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )

    # Load LoRA
    log.info("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(base_model, str(checkpoint))

    # Merge weights
    log.info("Merging LoRA weights...")
    merged_model = model.merge_and_unload()
    merged_model.eval()

    # Load tokenizer (optional metadata)
    try:
        tokenizer = AutoTokenizer.from_pretrained(str(checkpoint))
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)

    # Save .pt file
    output.parent.mkdir(parents=True, exist_ok=True)

    log.info(f"Saving .pt file → {output}")

    torch.save(
        {
            "model_state_dict": merged_model.state_dict(),
            "model_config": merged_model.config.to_dict(),
            "generation_config": merged_model.generation_config.to_dict()
            if hasattr(merged_model, "generation_config")
            else None,
            "tokenizer_vocab_size": len(tokenizer),
            "base_model": BASE_MODEL_ID,
            "checkpoint": str(checkpoint),
        },
        output,
    )

    log.info(f"Done. File size: {output.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()