import os
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from peft import PeftModel

# 1. Dynamically get the exact folder where this script is saved
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Construct absolute paths
base_model_name = "facebook/bart-base" 
adapter_path = os.path.join(script_dir, "checkpoint-3400")
export_path_pt = os.path.join(script_dir, "bart-merged-weights.pt")
tokenizer_export_path = os.path.join(script_dir, "exported-tokenizer")

if not os.path.isdir(adapter_path):
    raise FileNotFoundError(f"Could not find the folder at {adapter_path}.")

# 3. Load the tokenizer and models
tokenizer = AutoTokenizer.from_pretrained(adapter_path)
base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)
model = PeftModel.from_pretrained(base_model, adapter_path)

# 4. Merge the LoRA weights with the base model weights
print("Merging weights...")
merged_model = model.merge_and_unload()

# 5. Save the PyTorch state dictionary to a .pt file
print(f"Saving pure PyTorch weights to {export_path_pt}...")
torch.save(merged_model.state_dict(), export_path_pt)

# 6. Save the tokenizer normally (you will still need this to convert text to tokens in your app)
print(f"Saving tokenizer to {tokenizer_export_path}...")
tokenizer.save_pretrained(tokenizer_export_path)

print("Export complete!")