# Active model key — controls which pre-loaded model provides output at runtime.
# The UI reads this to set its initial state; call set_active_model() to switch.
# Options: "bart-xsum" | "cnn-dm"
ACTIVE_MODEL = "bart-xsum"

MODEL_PATHS = {
    "bart-xsum": "Train/runs/models/model_bart-xsum.pt",
    "cnn-dm":    "Train/runs/models/model_cnn-dm.pt",
}

MODEL_DISPLAY_NAMES = {
    "bart-xsum": "BART XSum",
    "cnn-dm":    "CNN / Daily Mail",
}

# Per-model generation length settings.
#
# bart-xsum  — min/max from working values in chat.py; optimal = typical XSum 1–2 sentence output
# cnn-dm     — min from testing_model.py (min_length=10); optimal from testing_model.py default
#              (max_new_tokens=64, "keep near max_target_len"); max from train_config.yaml
#              (generation_max_length: 128, used during eval)
MODEL_GENERATION = {
    "bart-xsum": {
        "min_length":     30,
        "optimal":        55,
        "max_new_tokens": 150,
    },
    "cnn-dm": {
        "min_length":     10,
        "optimal":        64,
        "max_new_tokens": 128,
    },
}

# Mutable at runtime — updated by set_active_model(), set_output_tokens(), set_max_attempts().
ACTIVE_MAX_NEW_TOKENS: int = MODEL_GENERATION[ACTIVE_MODEL]["optimal"]
ACTIVE_MIN_LENGTH: int = int(ACTIVE_MAX_NEW_TOKENS * 0.8)

# How many generation attempts are allowed before giving up (applies to both models).
# 1 = single attempt (no retry); 20 = up to 20 attempts.
MAX_ATTEMPTS: int = 10
