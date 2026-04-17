import argparse
import json
import matplotlib.pyplot as plt
import os

# Define the path to your JSON file. 
# Update 'trainer_state.json' if your file is named differently.

def plot_training_loss(json_path):
    if not os.path.exists(json_path):
        print(f"Error: Could not find the file '{json_path}'.")
        return

    # Read the JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract steps and loss values from log_history
    steps = []
    losses = []
    grad_norms = []
    
    for entry in data.get('log_history', []):
        # Make sure both 'step' and 'loss' keys exist in the current entry
        if 'step' in entry and 'loss' in entry and 'grad_norm' in entry:
            steps.append(entry['step'])
            losses.append(entry['loss'])
            grad_norms.append(entry['grad_norm'])

    if not (steps and losses):
        print("No loss data found in the JSON file.")
        return

    if not grad_norms:
        print("No gradient norm data found in the JSON file.")
        return

    # Get the latest step for the filename
    cp_step = steps[-1]

    # Create a figure with 2 subplots side-by-side (1 row, 2 columns)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Plot 1: Training Loss (Left) ---
    ax1.plot(steps, losses, marker='o', linestyle='-', color='#1f77b4', linewidth=2, label='Training Loss')
    ax1.set_title('Training Loss', fontsize=14, fontweight='bold', pad=10)
    ax1.set_xlabel('Global Step', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(fontsize=12)

    # --- Plot 2: Gradient Norm (Right) ---
    ax2.plot(steps, grad_norms, marker='s', linestyle='-', color='#ff7f0e', linewidth=2, label='Gradient Norm')
    ax2.set_title('Gradient Norm', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xlabel('Global Step', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Grad Norm', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(fontsize=12)
    
    # Adjust layout so nothing gets cut off
    plt.tight_layout()

    # --- Save to Train/plot relative to project root ---
    # This works as long as you run the script from the masv0 folder
    save_dir = os.path.join("Train", "plot")
    os.makedirs(save_dir, exist_ok=True)
    
    save_filename = f"plot_loss_and_grad_norm_step_{cp_step}.png"
    save_path = os.path.join(save_dir, save_filename)
    
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved plot to: {save_path}")

    # Display the plot
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot training loss and gradient norm from trainer_state.json")
    parser.add_argument(
        "--json_path",
        type=str,
        required=True,
        help="Path to the trainer_state.json file containing training logs.",
    )

    args = parser.parse_args()

    plot_training_loss(args.json_path)