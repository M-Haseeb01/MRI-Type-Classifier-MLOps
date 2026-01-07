from flask import Flask, render_template, request, jsonify, redirect, url_for
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image, ImageOps
import io
import json
import os
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)

# Configuration
IMG_SIZE = 224
MODEL_PATH = 'brain_tumor_model.h5'
CLASS_INDICES_PATH = 'class_indices.json'
MODEL_VERSION = 'v1.0'
DB_PATH = 'predictions.db'
HISTORY_IMAGES_DIR = 'history_images'

# Load the trained model
print("Loading model...")
model = keras.models.load_model(MODEL_PATH)
print("Model loaded successfully!")

# Load class indices
with open(CLASS_INDICES_PATH, 'r') as f:
    class_names = json.load(f)
    # Convert keys to integers
    class_names = {int(k): v for k, v in class_names.items()}

print("Class names:", class_names)

# Initialize database
def init_db():
    """Initialize the SQLite database for prediction history"""
    os.makedirs(HISTORY_IMAGES_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL,
            model_version TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(image_filename, prediction, confidence):
    """Save a prediction to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO predictions (image_filename, prediction, confidence, timestamp, model_version)
        VALUES (?, ?, ?, ?, ?)
    ''', (image_filename, prediction, confidence, timestamp, MODEL_VERSION))
    conn.commit()
    conn.close()

def get_all_predictions():
    """Retrieve all predictions from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY timestamp DESC')
    predictions = cursor.fetchall()
    conn.close()
    return predictions

def clear_all_predictions():
    """Clear all predictions from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions')
    conn.commit()
    conn.close()
    
    # Clear all images in history_images directory
    for filename in os.listdir(HISTORY_IMAGES_DIR):
        file_path = os.path.join(HISTORY_IMAGES_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def preprocess_image(image_bytes):
    """Preprocess the uploaded image for prediction"""
    # Open image
    img = Image.open(io.BytesIO(image_bytes))
    
    # 1. Convert to Grayscale (remove color noise from internet images)
    img = img.convert('L')
    
    # 2. Enhance Contrast (make it look more like an MRI)
    img = ImageOps.autocontrast(img)
    
    # 3. Convert back to RGB (Model expects 3 channels)
    img = img.convert('RGB')
    
    # Resize to model input size
    img = img.resize((IMG_SIZE, IMG_SIZE))
    
    # Convert to array and normalize
    img_array = np.array(img)
    img_array = img_array / 255.0
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

@app.route('/')
def home():
    """Render the home page"""
    return render_template('home.html')

@app.route('/predict')
def predict_page():
    """Render the prediction page"""
    return render_template('predict.html')

@app.route('/about-model')
def about():
    """Render the about/info page"""
    return render_template('about.html')

@app.route('/history')
def history():
    """Render the prediction history page"""
    predictions = get_all_predictions()
    return render_template('history.html', predictions=predictions)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Handle image upload and make prediction"""
    try:
        # Check if image was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and preprocess image
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        # Make prediction
        predictions = model.predict(processed_image, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # Get class name
        predicted_class = class_names[predicted_class_idx]
        
        # Format class name for display
        class_display = predicted_class.replace('_', ' ').title()
        if predicted_class == 'notumor':
            class_display = 'No Tumor'
        
        # Save uploaded image with unique filename
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        image_path = os.path.join(HISTORY_IMAGES_DIR, unique_filename)
        
        # Save the image
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(image_path)
        
        # Save prediction to database
        save_prediction(unique_filename, class_display, confidence)
        
        # Get all class probabilities
        all_predictions = {}
        for idx, prob in enumerate(predictions[0]):
            class_name = class_names[idx].replace('_', ' ').title()
            if class_names[idx] == 'notumor':
                class_name = 'No Tumor'
            all_predictions[class_name] = float(prob)
        
        # Prepare response
        response = {
            'success': True,
            'predicted_class': class_display,
            'confidence': confidence,
            'all_predictions': all_predictions
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear all prediction history"""
    try:
        clear_all_predictions()
        return jsonify({'success': True, 'message': 'History cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs(HISTORY_IMAGES_DIR, exist_ok=True)
    
    # Initialize database
    init_db()
    
    print("\n" + "="*50)
    print("Brain Tumor Classification Web App")
    print("="*50)
    print("\nServer starting...")
    print("Open your browser and go to: http://localhost:5000")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
