"""
test_mps.py
Optimized evaluation script for testing BART LoRA checkpoints on Mac M1 (MPS) 
or resource-constrained hardware.
"""
import argparse
import gc
import torch
import evaluate
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GenerationConfig
from peft import PeftConfig, PeftModel
from datasets import load_dataset
from tqdm import tqdm

def get_device_and_dtype():
    """Safely determines the best available hardware and precision."""
    if torch.backends.mps.is_available():
        print("Hardware: Apple Silicon (MPS) detected.")
        return torch.device("mps"), torch.float16
    elif torch.cuda.is_available():
        print("Hardware: NVIDIA GPU (CUDA) detected.")
        return torch.device("cuda"), torch.float16
    else:
        print("Hardware: CPU detected. Forcing FP32 (FP16 not supported natively).")
        return torch.device("cpu"), torch.float32

def clear_memory():
    """Forces garbage collection and clears backend cache to prevent OOM."""
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

def main(args):
    device, dtype = get_device_and_dtype()

    print(f"\nLoading adapter and base model from: {args.checkpoint}...")

    # 1. Explicit Loading (Safer for MPS than device_map="auto")
    peft_config = PeftConfig.from_pretrained(args.checkpoint)
    base_model_id = peft_config.base_model_name_or_path
    
    print(f"Resolved base model: {base_model_id}")
    
    # Load base model directly to memory in the correct precision
    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model_id,
        torch_dtype=dtype,
        low_cpu_mem_usage=True
    )
    
    # Wrap with LoRA and push explicitly to the target device
    model = PeftModel.from_pretrained(base_model, args.checkpoint)
    model.to(device)
    model.eval()

    try:
        tokenizer = AutoTokenizer.from_pretrained(args.checkpoint)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(base_model_id)

    # 2. Modern Generation Configuration
    gen_config = GenerationConfig(
        num_beams=4,
        min_length=30,
        max_length=130,
        early_stopping=True,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        bos_token_id=tokenizer.bos_token_id
    )

    # 3. Load dataset and metrics
    print("\nLoading CNN/DailyMail dataset and ROUGE metric...")
    dataset = load_dataset("cnn_dailymail", "3.0.0", split="validation")
    rouge = evaluate.load("rouge")

    # 4. Qualitative Test (Vibe Check)
    print("\n" + "="*50)
    print("QUALITATIVE TEST (1 Sample Article-Summary Pair)")
    print("="*50)
    
    sample = dataset[0]
    inputs = tokenizer(sample["article"], return_tensors="pt", max_length=1024, truncation=True).to(device)
    
    # torch.inference_mode() is faster and lighter than torch.no_grad()
    with torch.inference_mode():
        summary_ids = model.generate(**inputs, generation_config=gen_config)
    
    generated_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    print(f"\n[ARTICLE SNIPPET]:\n{sample['article'][:400]}...\n")
    print(f"[REFERENCE SUMMARY]:\n{sample['highlights']}\n")
    print(f"[MODEL GENERATED]:\n{generated_summary}\n")

    # 5. Quantitative Test (Batched Inference)
    print("="*50)
    print(f"QUANTITATIVE TEST (ROUGE on {args.samples} samples, Batch Size: {args.batch_size})")
    print("="*50)
    
    test_subset = dataset.select(range(args.samples))
    generated_summaries = []
    reference_summaries = test_subset["highlights"]

    # Batched inference loop
    for i in tqdm(range(0, len(test_subset), args.batch_size), desc="Generating summaries"):
        batch = test_subset[i : i + args.batch_size]
        
        inputs = tokenizer(
            batch["article"], 
            return_tensors="pt", 
            max_length=1024, 
            truncation=True, 
            padding=True 
        ).to(device)
        
        with torch.inference_mode():
            summary_ids = model.generate(**inputs, generation_config=gen_config)
        
        gen_texts = tokenizer.batch_decode(summary_ids, skip_special_tokens=True)
        generated_summaries.extend(gen_texts)
        
        # Aggressively clear memory after each batch to help weaker hardware
        del inputs
        del summary_ids
        clear_memory()

    # Compute and print results
    results = rouge.compute(predictions=generated_summaries, references=reference_summaries)
    
    print("\n[ROUGE RESULTS]:")
    for key, value in results.items():
        print(f"{key.upper()}: {value * 100:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test a BART LoRA checkpoint on M1/MPS or low-spec hardware")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to the LoRA checkpoint directory")
    parser.add_argument("--samples", type=int, default=20, help="Number of samples to evaluate")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size (keep low for weaker hardware)")
    
    args = parser.parse_args()
    main(args)