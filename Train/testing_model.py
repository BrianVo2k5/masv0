import torch
import argparse
import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def main():
    parser = argparse.ArgumentParser(
        description="Test LED-base-16384 summarizer .pt model"
    )
    parser.add_argument("--model_path", type=str, required=True, help="Path to exported .pt weights")
    parser.add_argument("--model_type", type=str, default="allenai/led-base-16384", help="Base architecture")
    parser.add_argument("--file_path", type=str, required=True, help="Input text file")
    parser.add_argument("--max_new_tokens", type=int, default=64,
                        help="Max summary tokens — keep near max_target_len used in training (default 64)")
    parser.add_argument("--num_beams", type=int, default=4)
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return

    device = get_device()
    print(f"Device: {device}")

    with open(args.file_path, "r", encoding="utf-8") as f:
        input_text = f.read()

    print("Loading tokenizer and model...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model_type)
        model = AutoModelForSeq2SeqLM.from_pretrained(args.model_type)
    except Exception as e:
        print(f"Error loading base model/tokenizer: {e}")
        return

    try:
        state_dict = torch.load(args.model_path, map_location="cpu", weights_only=False)
        if "model_state_dict" in state_dict:
            state_dict = state_dict["model_state_dict"]
        model.load_state_dict(state_dict)
        print("Weights loaded successfully.")
    except Exception as e:
        print(f"Error loading weights: {e}")
        return

    model.to(device)
    model.eval()

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=16384,
        truncation=True,
    )
    input_len = inputs["input_ids"].shape[1]
    original_len = len(tokenizer(input_text, add_special_tokens=False)["input_ids"])
    if original_len > 16384:
        print(f"Warning: input was {original_len} tokens, truncated to 16384")
    else:
        print(f"Input length: {input_len} tokens")

    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    # LED requires global attention; BOS token gets it at minimum
    global_attention_mask = torch.zeros_like(attention_mask)
    global_attention_mask[:, 0] = 1

    print(f"Generating summary (max_new_tokens={args.max_new_tokens}, beams={args.num_beams})...")

    with torch.no_grad():
        summary_ids = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            global_attention_mask=global_attention_mask,
            max_new_tokens=args.max_new_tokens,
            min_length=10,
            num_beams=args.num_beams,
            length_penalty=2.0,
            no_repeat_ngram_size=3,
            early_stopping=True,
            pad_token_id=tokenizer.pad_token_id,
        )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    print(f"\n--- Summary ({len(summary_ids[0])} tokens) ---")
    print(summary)


if __name__ == "__main__":
    main()
