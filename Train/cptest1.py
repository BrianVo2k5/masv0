import argparse
import torch
import evaluate
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from peft import PeftModel
from datasets import load_dataset
from tqdm import tqdm

def main(args):
    print(f"Loading base model and checkpoint from: {args.checkpoint}...")

    # 1. Load models — read the base model from the adapter config so the
    # tester always matches whatever was used at training time.
    from peft import PeftConfig
    peft_config = PeftConfig.from_pretrained(args.checkpoint)
    base_model_id = peft_config.base_model_name_or_path
    print(f"Resolved base model from adapter config: {base_model_id}")

    tokenizer = AutoTokenizer.from_pretrained(base_model_id)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_id, device_map="auto")
    model = PeftModel.from_pretrained(base_model, args.checkpoint)
    
    # Set to evaluation mode
    model.eval()

    # 2. Load dataset and metrics
    print("Loading CNN-DailyMail dataset and ROUGE metric...")
    dataset = load_dataset("cnn_dailymail", "3.0.0", split="validation")
    rouge = evaluate.load("rouge")

    # 3. Qualitative Test (Vibe Check on 1 sample)
    print("\n" + "="*50)
    print("QUALITATIVE TEST (VIBE CHECK)")
    print("="*50)
    
    sample = dataset[0]
    inputs = tokenizer(sample["article"], return_tensors="pt", max_length=1024, truncation=True).to(model.device)
    
    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"], 
            num_beams=4, 
            min_length=30, 
            max_length=130, 
            early_stopping=True
        )
    
    generated_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    print(f"\n[ARTICLE SNIPPET]:\n{sample['article'][:400]}...\n")
    print(f"[REFERENCE SUMMARY]:\n{sample['highlights']}\n")
    print(f"[MODEL GENERATED]:\n{generated_summary}\n")

    # 4. Quantitative Test (ROUGE Score)
    print("="*50)
    print(f"QUANTITATIVE TEST (ROUGE on {args.samples} samples)")
    print("="*50)
    
    test_subset = dataset.select(range(args.samples))
    generated_summaries = []
    reference_summaries = []

    for item in tqdm(test_subset, desc="Generating summaries"):
        inputs = tokenizer(item["article"], return_tensors="pt", max_length=1024, truncation=True).to(model.device)
        
        with torch.no_grad():
            summary_ids = model.generate(
                inputs["input_ids"], 
                num_beams=4, 
                min_length=30, 
                max_length=130, 
                early_stopping=True
            )
        
        gen_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        generated_summaries.append(gen_text)
        reference_summaries.append(item["highlights"])

    # Compute and print results
    results = rouge.compute(predictions=generated_summaries, references=reference_summaries)
    
    print("\n[ROUGE RESULTS]:")
    for key, value in results.items():
        # Evaluate returns decimals (e.g., 0.44), multiply by 100 for standard ROUGE format
        print(f"{key.upper()}: {value * 100:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test a BART LoRA checkpoint on CNN-DailyMail")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to the LoRA checkpoint directory")
    parser.add_argument("--samples", type=int, default=20, help="Number of samples to evaluate for ROUGE (default: 20)")
    
    args = parser.parse_args()
    main(args)