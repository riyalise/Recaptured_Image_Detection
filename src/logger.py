import logging
import os
from datetime import datetime

# ── Read log paths ────────────────────────────────────────────────────
APP_LOG_PATH         = "data/logs/app.log"
PREDICTIONS_LOG_PATH = "data/logs/predictions.log"

# ── Shared formatter ──────────────────────────────────────────────────
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(filename)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ─────────────────────────────────────────────────────────────────────
# APP LOGGER
# General application events — startup, errors, warnings
# ─────────────────────────────────────────────────────────────────────
def get_app_logger():
    logger = logging.getLogger("app_logger")

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler — writes to app.log
    file_handler = logging.FileHandler(APP_LOG_PATH)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler — prints to terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ─────────────────────────────────────────────────────────────────────
# PREDICTION LOGGER
# One entry per image submission — the audit trail
# ─────────────────────────────────────────────────────────────────────
def get_prediction_logger():
    logger = logging.getLogger("prediction_logger")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # File handler only — predictions don't need to print to terminal
    file_handler = logging.FileHandler(PREDICTIONS_LOG_PATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# ─────────────────────────────────────────────────────────────────────
# Initialise both loggers at import time
# ─────────────────────────────────────────────────────────────────────
app_logger        = get_app_logger()
prediction_logger = get_prediction_logger()