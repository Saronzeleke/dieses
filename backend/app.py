from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import numpy as np
from PIL import Image
import tensorflow as tf
import os
import logging

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE = os.getenv("DATABASE", "crop_disease.db")

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                feedback TEXT
            )
            """
        )
        conn.commit()

init_db()

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Crop Disease Detection API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

MODEL_PATH = os.getenv("MODEL_PATH", "crop_disease_detection_model.keras")  # Adjusted for backend folder
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

CLASS_LABELS = ["Healthy", "Powdery Mildew", "Leaf Spot", "Blight", "Rust"]
TREATMENTS = {
    "Powdery Mildew": "Apply fungicides like sulfur or potassium bicarbonate.",
    "Leaf Spot": "Remove infected leaves and apply copper-based fungicides.",
    "Blight": "Use fungicides and ensure proper crop rotation.",
    "Rust": "Apply fungicides and remove infected plants.",
    "Healthy": "No treatment needed. Your crop is healthy!",
}

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image, target_size=(224, 224)):
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size)
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

def save_prediction(filename, disease, confidence):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """
            INSERT INTO predictions (filename, disease, confidence)
            VALUES (?, ?, ?)
            """,
            (filename, disease, confidence),
        )
        conn.commit()

@app.route("/predict", methods=["POST"])
@limiter.limit("10 per minute")
def predict():
    if "file" not in request.files:
        logger.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        logger.error("No file selected")
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        logger.error(f"Invalid file type: {file.filename}")
        return jsonify({"error": "Invalid file type. Only PNG, JPG, and JPEG are allowed."}), 400

    if not model:
        logger.error("Model not loaded")
        return jsonify({"error": "Model not available"}), 500

    try:
        image = Image.open(file.stream)
        processed_image = preprocess_image(image)
        logger.info(f"Processed image shape: {processed_image.shape}")
        predictions = model.predict(processed_image)
        logger.info(f"Model predictions: {predictions}")

        predicted_class_index = np.argmax(predictions, axis=1)[0]
        predicted_class = CLASS_LABELS[predicted_class_index]
        confidence = float(predictions[0][predicted_class_index])

        if confidence < 0.5:
            predicted_class = "Healthy"
            confidence = 1.0

        logger.info(f"Predicted class: {predicted_class}, Confidence: {confidence}")

        save_prediction(file.filename, predicted_class, confidence)

        return jsonify({
            "predicted_disease": predicted_class,
            "confidence": confidence,
            "treatment": TREATMENTS.get(predicted_class, "No treatment information available."),
        })

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    if not data or "id" not in data or "feedback" not in data:
        return jsonify({"error": "Invalid feedback data"}), 400

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM predictions WHERE id = ?", (data["id"],))
            if not cursor.fetchone():
                return jsonify({"error": "Invalid prediction ID"}), 404

            cursor.execute(
                """
                UPDATE predictions
                SET feedback = ?
                WHERE id = ?
                """,
                (data["feedback"], data["id"]),
            )
            conn.commit()

        return jsonify({"message": "Feedback submitted successfully!"})

    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/static/swagger.json")
def serve_swagger():
    return send_from_directory("static", "swagger.json")

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)