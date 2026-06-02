import os
import torch
from PIL import Image
from dotenv import load_dotenv
from src.transforms import eval_tf
from src.architecture import model, device
from src.logger import app_logger, prediction_logger

# ── Load thresholds from .env ─────────────────────────────────────────
load_dotenv()

ACCEPT_THRESHOLD = float(os.getenv("ACCEPT_THRESHOLD", 0.25))
REJECT_THRESHOLD = float(os.getenv("REJECT_THRESHOLD", 0.75))

app_logger.info(f"Thresholds loaded — Accept: {ACCEPT_THRESHOLD} | Reject: {REJECT_THRESHOLD}")

CLASSES = ["original", "photo_of_photo"]


# ─────────────────────────────────────────────────────────────────────
# IMAGE VALIDATION
# ─────────────────────────────────────────────────────────────────────
def validate_image(image_path):
    try:
        img = Image.open(image_path)
        img.verify()
        return True, None
    except Exception as e:
        app_logger.warning(f"Invalid image file: {image_path} | Reason: {e}")
        return False, str(e)


# ─────────────────────────────────────────────────────────────────────
# PREPROCESSING
# ─────────────────────────────────────────────────────────────────────
def preprocess(image_path):
    img = Image.open(image_path).convert("RGB")
    tensor = eval_tf(img).unsqueeze(0).to(device)
    return tensor


# ─────────────────────────────────────────────────────────────────────
# CORE PREDICTION
# ─────────────────────────────────────────────────────────────────────
def predict(tensor):
    with torch.no_grad():
        logit = model(tensor)
        prob  = torch.sigmoid(logit).item()
    return prob


# ─────────────────────────────────────────────────────────────────────
# DECISION LOGIC
# ─────────────────────────────────────────────────────────────────────
def make_decision(prob):
    if prob < ACCEPT_THRESHOLD:
        return CLASSES[0], "ACCEPT"
    elif prob > REJECT_THRESHOLD:
        return CLASSES[1], "REJECT"
    else:
        return "uncertain", "MANUAL_REVIEW"


# ─────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# Called by routes.py for every incoming image
# ─────────────────────────────────────────────────────────────────────
def predict_image(image_path, filename="unknown"):
    app_logger.info(f"Processing image: {filename}")

    # Step 1 — validate
    is_valid, error = validate_image(image_path)
    if not is_valid:
        app_logger.error(f"Validation failed for: {filename} | {error}")
        return {
            "filename": filename,
            "label":    None,
            "prob":     None,
            "decision": "ERROR",
            "error":    f"Invalid image: {error}"
        }

    # Step 2 — preprocess
    try:
        tensor = preprocess(image_path)
    except Exception as e:
        app_logger.error(f"Preprocessing failed for: {filename} | {e}")
        return {
            "filename": filename,
            "label":    None,
            "prob":     None,
            "decision": "ERROR",
            "error":    f"Preprocessing failed: {e}"
        }

    # Step 3 — predict
    try:
        prob = predict(tensor)
    except Exception as e:
        app_logger.error(f"Inference failed for: {filename} | {e}")
        return {
            "filename": filename,
            "label":    None,
            "prob":     None,
            "decision": "ERROR",
            "error":    f"Inference failed: {e}"
        }

    # Step 4 — decide
    label, decision = make_decision(prob)

    # Step 5 — log the prediction audit trail
    prediction_logger.info(
        f"{decision} | label: {label} | prob: {prob:.4f} | file: {filename}"
    )

    app_logger.info(
        f"Prediction complete — {decision} | prob: {prob:.4f} | file: {filename}"
    )

    return {
        "filename": filename,
        "label":    label,
        "prob":     round(prob, 4),
        "decision": decision,
        "error":    None
    }