import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from src.logger import app_logger
from src.predictor import predict_image

# ── Load environment variables ────────────────────────────────────────
load_dotenv()

FLASK_HOST     = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT     = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG    = os.getenv("FLASK_DEBUG", "False").lower() == "true"
MAX_FILE_SIZE  = int(os.getenv("MAX_FILE_SIZE_MB", 5)) * 1024 * 1024
ALLOWED_EXT    = set(os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png").split(","))
UPLOAD_FOLDER  = "data/uploads"

# ─────────────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="frontend")
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app_logger.info("Flask app initialised")
app_logger.info(f"Host: {FLASK_HOST} | Port: {FLASK_PORT} | Debug: {FLASK_DEBUG}")


# ─────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT
    )


def secure_upload_filename(filename):
    return f"{uuid.uuid4().hex}_{secure_filename(filename)}"


# ─────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────

# ── Serve frontend ────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("frontend", filename)


# ── Health check ──────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    app_logger.info("Health check called")
    return jsonify({
        "status":  "ok",
        "model":   "ResNet-50",
        "device":  os.getenv("DEVICE", "cpu")
    }), 200


# ── Prediction endpoint ───────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    app_logger.info("Prediction request received")

    # ── 1. Check file exists in request ──────────────────────────────
    if "file" not in request.files:
        app_logger.warning("No file field in request")
        return jsonify({
            "error": "No file uploaded. Include a file field in the request."
        }), 400

    file = request.files["file"]

    # ── 2. Check file was actually selected ──────────────────────────
    if file.filename == "":
        app_logger.warning("Empty filename received")
        return jsonify({"error": "No file selected"}), 400

    # ── 3. Check file extension ───────────────────────────────────────
    if not allowed_file(file.filename):
        app_logger.warning(f"Rejected file type: {file.filename}")
        return jsonify({
            "error": f"File type not allowed. Accepted types: {', '.join(ALLOWED_EXT)}"
        }), 415

    # ── 4. Save uploaded file persistently ──────────────────────────
    original_filename = file.filename
    saved_filename    = secure_upload_filename(original_filename)
    saved_path        = os.path.join(UPLOAD_FOLDER, saved_filename)

    try:
        file.save(saved_path)
        app_logger.info(f"File saved: {saved_filename}")
    except Exception as e:
        app_logger.error(f"Failed to save uploaded file: {e}")
        return jsonify({"error": "Failed to save file on server"}), 500

    # ── 5. Run prediction ─────────────────────────────────────────────
    result = predict_image(saved_path, filename=original_filename)

    # ── 6. Handle prediction error ────────────────────────────────────
    if result["decision"] == "ERROR":
        app_logger.error(f"Prediction error: {result['error']}")
        return jsonify({"error": result["error"]}), 422

    # ── 7. Return result ──────────────────────────────────────────────
    result["saved_filename"] = saved_filename
    result["saved_path"]     = os.path.relpath(saved_path, start=os.getcwd())
    app_logger.info(f"Returning result: {result['decision']} | {result['prob']} | saved: {saved_filename}")
    return jsonify(result), 200


# ─────────────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────────────────────────────
@app.errorhandler(413)
def file_too_large(e):
    app_logger.warning("File too large rejected")
    return jsonify({
        "error": f"File too large. Maximum size is {os.getenv('MAX_FILE_SIZE_MB', 5)}MB"
    }), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    app_logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app_logger.info("Starting Recaptured Image Detection Server...")
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )