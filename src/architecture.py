import os
import torch
import torch.nn as nn
from torchvision import models
from dotenv import load_dotenv
from src.logger import app_logger

# ── Load environment variables ────────────────────────────────────────
load_dotenv()

DEVICE     = os.getenv("DEVICE", "cpu")
MODEL_PATH = os.getenv("MODEL_PATH", "model/attendance_model.pth")

# ─────────────────────────────────────────────────────────────────────
# DEVICE SETUP
# ─────────────────────────────────────────────────────────────────────
device = torch.device(DEVICE)
app_logger.info(f"Device set to: {device}")


# ─────────────────────────────────────────────────────────────────────
# MODEL DEFINITION
# Must be identical to the architecture trained in Colab
# ─────────────────────────────────────────────────────────────────────
def build_model():
    app_logger.info("Building ResNet-50 architecture...")

    model = models.resnet50(weights=None)

    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.fc.in_features, 1)
    )

    return model


# ─────────────────────────────────────────────────────────────────────
# WEIGHT LOADING
# ─────────────────────────────────────────────────────────────────────
def load_model():
    app_logger.info(f"Loading model weights from: {MODEL_PATH}")

    if not os.path.exists(MODEL_PATH):
        app_logger.error(f"Model file not found at: {MODEL_PATH}")
        raise FileNotFoundError(
            f"Model weights not found at {MODEL_PATH}. "
            f"Download the .pth file from Colab and place it in the model/ folder."
        )

    model = build_model()

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
        weights_only=True
    )

    # Handle both save formats
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
        app_logger.info(f"Classes: {checkpoint.get('classes', 'not stored in checkpoint')}")
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()

    app_logger.info("Model loaded and set to eval mode successfully")
    return model, device


# ─────────────────────────────────────────────────────────────────────
# SINGLETON — load once, reuse everywhere
# ─────────────────────────────────────────────────────────────────────
try:
    model, device = load_model()
except Exception as e:
    app_logger.error(f"Failed to load model: {e}")
    raise