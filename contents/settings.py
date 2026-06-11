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
