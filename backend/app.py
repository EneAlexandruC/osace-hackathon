"""
Flask API for Robot vs Human Image Classification
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
import io
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import (
    MODEL_PATH, MODEL_INPUT_SIZE, CLASS_NAMES, UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
)
from backend.supabase_db import SupabaseDB

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables
model = None
db = None


def load_model():
    """Load the trained model"""
    global model
    try:
        if not MODEL_PATH.exists():
            print(f"⚠ WARNING: Model file not found at {MODEL_PATH}")
            print("Please train the model first using train.py")
            return False
        
        print(f"Loading model from {MODEL_PATH}...")
        model = keras.models.load_model(MODEL_PATH)
        print("✓ Model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False


def initialize_database():
    """Initialize Supabase database connection"""
    global db
    try:
        db = SupabaseDB()
        print("✓ Database connection initialized!")
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not connect to database: {e}")
        return False


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_bytes):
    """
    Preprocess image for prediction
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Preprocessed image array ready for prediction
    """
    # Open image
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize to model input size
    image = image.resize(MODEL_INPUT_SIZE)
    
    # Convert to array and normalize
    image_array = np.array(image) / 255.0
    
    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)
    
    return image_array


@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'database_connected': db is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict image class
    
    Expected: multipart/form-data with 'image' field
    Returns: JSON with predicted class and confidence
    """
    # Check if model is loaded
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.'
        }), 503
    
    # Check if image is in request
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Read and preprocess image
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        # Make prediction
        predictions = model.predict(processed_image, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        predicted_class = CLASS_NAMES[predicted_class_idx]
        
        # Get all class probabilities
        class_probabilities = {
            CLASS_NAMES[i]: float(predictions[0][i])
            for i in range(len(CLASS_NAMES))
        }
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save image to disk
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Save to database
        if db is not None:
            try:
                db.save_prediction(unique_filename, predicted_class, confidence)
            except Exception as e:
                print(f"Warning: Could not save to database: {e}")
        
        # Return response
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': class_probabilities,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({
            'error': f'Prediction failed: {str(e)}'
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get prediction history from database"""
    if db is None:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        limit = request.args.get('limit', 100, type=int)
        predictions = db.get_all_predictions(limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({
            'error': f'Could not retrieve history: {str(e)}'
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get prediction statistics"""
    if db is None:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'error': f'Could not retrieve statistics: {str(e)}'
        }), 500


@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """Get information about the loaded model"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        return jsonify({
            'success': True,
            'model_path': str(MODEL_PATH),
            'input_size': MODEL_INPUT_SIZE,
            'classes': CLASS_NAMES,
            'num_classes': len(CLASS_NAMES),
            'total_parameters': int(model.count_params())
        })
    except Exception as e:
        return jsonify({
            'error': f'Could not retrieve model info: {str(e)}'
        }), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'error': f'File too large. Maximum size: {MAX_CONTENT_LENGTH / (1024*1024):.0f}MB'
    }), 413


def main():
    """Main function to run the Flask app"""
    print("\n" + "="*60)
    print("ROBOT VS HUMAN CLASSIFIER - API SERVER")
    print("="*60)
    
    # Load model
    model_loaded = load_model()
    if not model_loaded:
        print("\n⚠ WARNING: Starting server without model!")
        print("Train the model first: python model/train.py")
    
    # Initialize database
    db_connected = initialize_database()
    if not db_connected:
        print("\n⚠ WARNING: Starting server without database connection!")
    
    # Start server
    print("\n" + "="*60)
    print(f"Starting Flask server on http://{FLASK_HOST}:{FLASK_PORT}")
    print("="*60)
    print("\nAvailable endpoints:")
    print("  GET  /                    - Main web interface")
    print("  GET  /health              - Health check")
    print("  POST /api/predict         - Make prediction")
    print("  GET  /api/history         - Get prediction history")
    print("  GET  /api/statistics      - Get statistics")
    print("  GET  /api/model-info      - Get model information")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")
    
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )


if __name__ == '__main__':
    main()
