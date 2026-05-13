import argparse
import logging
from pathlib import Path

import torch
from peft import PeftConfig, PeftModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

DEFAULT_CHECKPOINT = Path(__file__).parent / "runs/bart-lora/"
DEFAULT_OUTPUT = Path(__file__).parent / "runs/bart-lora/model.pt"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT), help="Path to LoRA checkpoint directory")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output .pt file path")
    args = parser.parse_args()

    checkpoint = Path(args.checkpoint)
    output = Path(args.output)

    if not checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")

    if torch.backends.mps.is_available():
        device = torch.device("mps")
        dtype = torch.float16
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        dtype = torch.float16
    else:
        device = torch.device("cpu")
        dtype = torch.float32

    log.info(f"Device: {device}  |  dtype: {dtype}")

    peft_config = PeftConfig.from_pretrained(checkpoint)
    base_model_id = peft_config.base_model_name_or_path
    log.info(f"Base model: {base_model_id}")

    log.info("Loading base model …")
    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model_id,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )

    log.info(f"Loading LoRA adapter from {checkpoint} …")
    model = PeftModel.from_pretrained(base_model, str(checkpoint))

    log.info("Merging LoRA weights into base model …")
    merged_model = model.merge_and_unload()
    merged_model.eval()

    try:
        tokenizer = AutoTokenizer.from_pretrained(str(checkpoint))
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(base_model_id)

    output.parent.mkdir(parents=True, exist_ok=True)
    log.info(f"Saving merged state dict → {output}")
    torch.save(
        {
            "model_state_dict": merged_model.state_dict(),
            "model_config": merged_model.config.to_dict(),
            "tokenizer_vocab_size": len(tokenizer),
            "base_model": base_model_id,
            "checkpoint": str(checkpoint),
        },
        output,
    )
    log.info(f"Done. File size: {output.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
