import torch
import argparse
import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def main():
    parser = argparse.ArgumentParser(
        description="Test LED-base-16384 summarizer .pt model"
    )

    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to fine-tuned .pt weights"
    )

    parser.add_argument(
        "--model_type",
        type=str,
        default="allenai/led-base-16384",
        help="Base architecture"
    )

    parser.add_argument(
        "--file_path",
        type=str,
        required=True,
        help="Input text file"
    )

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(args.file_path, "r", encoding="utf-8") as f:
        input_text = f.read()

    print("Loading tokenizer and model...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(args.model_type)

        model = AutoModelForSeq2SeqLM.from_pretrained(args.model_type)

        model.resize_token_embeddings(len(tokenizer))

    except Exception as e:
        print(f"Error loading base model/tokenizer: {e}")
        return

    try:
        state_dict = torch.load(
            args.model_path,
            map_location=device
        )

        if "model_state_dict" in state_dict:
            state_dict = state_dict["model_state_dict"]

        model.load_state_dict(state_dict)

        print("Weights loaded successfully!")

    except Exception as e:
        print(f"Error loading weights: {e}")
        return

    model.to(device)
    model.eval()

    print("Tokenizing input text...")

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=16384,
        truncation=True
    )

    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    global_attention_mask = torch.zeros_like(attention_mask)
    global_attention_mask[:, 0] = 1

    print("Generating summary...")

    with torch.no_grad():

        summary_ids = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            global_attention_mask=global_attention_mask,
            max_new_tokens=250,
            min_length=30,
            num_beams=2,
            no_repeat_ngram_size=3,
            early_stopping=True,
            pad_token_id=tokenizer.pad_token_id
        )

    summary = tokenizer.decode(
        summary_ids[0],
        skip_special_tokens=True
    )

    print("\n--- AI Summary ---")
    print(summary)


if __name__ == "__main__":
    main()