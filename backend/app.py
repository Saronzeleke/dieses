from flask import Flask, request, jsonify
import tensorflow as tf
from PIL import Image
import numpy as np
import io

app = Flask(__name__)
model = tf.keras.models.load_model('backend/disease_detection_model.keras')

# Preprocess the uploaded image
def preprocess_image(image):
    img = Image.open(io.BytesIO(image)).resize((128, 128))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

@app.route('/api/detect-disease', methods=['POST'])
def detect_disease():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file'].read()
    img = preprocess_image(file)
    prediction = model.predict(img)
    predicted_class = np.argmax(prediction, axis=1)[0]
    classes = list(train_generator.class_indices.keys())  # Replace with actual class names
    return jsonify({"disease": classes[predicted_class]})

if __name__ == '__main__':
    app.run(debug=True)