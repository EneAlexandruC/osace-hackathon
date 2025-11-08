"""
Flask API for Robot vs Human Image Classification
Supports both Keras (.h5) and PyTorch (.pth) models
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
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
    MODEL_PATH, MODEL_TYPE, MODEL_INPUT_SIZE, CLASS_NAMES, UPLOAD_FOLDER,
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
model_type = None  # 'keras' or 'pytorch'
db = None


def load_model():
    """Load the trained model (supports both Keras and PyTorch)"""
    global model, model_type
    
    try:
        if not MODEL_PATH.exists():
            print(f"⚠ WARNING: Model file not found at {MODEL_PATH}")
            print("Please train the model first using train.py")
            return False
        
        # Detect model type
        model_extension = MODEL_PATH.suffix.lower()
        
        if MODEL_TYPE == "auto":
            if model_extension in ['.h5', '.keras']:
                model_type = 'keras'
            elif model_extension in ['.pth', '.pt']:
                model_type = 'pytorch'
            else:
                print(f"⚠ WARNING: Unknown model extension: {model_extension}")
                return False
        else:
            model_type = MODEL_TYPE
        
        print(f"Loading {model_type} model from {MODEL_PATH}...")
        
        if model_type == 'keras':
            import tensorflow as tf
            from tensorflow import keras
            model = keras.models.load_model(MODEL_PATH)
            print("✓ Keras model loaded successfully!")
            
        elif model_type == 'pytorch':
            import torch
            import torch.nn as nn
            
            # Load the model state dict
            model = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
            
            # If it's just a state dict, you need to instantiate the model architecture
            if isinstance(model, dict):
                print("⚠ WARNING: Loaded state_dict. You need to define the model architecture.")
                print("Please provide the full model or update the code with your model architecture.")
                return False
            
            model.eval()  # Set to evaluation mode
            print("✓ PyTorch model loaded successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
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
    Preprocess image for prediction (works for both Keras and PyTorch)
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Preprocessed image array/tensor ready for prediction
    """
    # Open image
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize to model input size
    image = image.resize(MODEL_INPUT_SIZE)
    
    if model_type == 'keras':
        # Keras preprocessing
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        return image_array
        
    elif model_type == 'pytorch':
        # PyTorch preprocessing
        import torch
        from torchvision import transforms
        
        # Define transforms
        transform = transforms.Compose([
            transforms.ToTensor(),  # Converts to [0, 1] and changes to CxHxW
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        image_tensor = transform(image)
        image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
        return image_tensor


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
        
        # Make prediction based on model type
        if model_type == 'keras':
            predictions = model.predict(processed_image, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            
            # Get all class probabilities
            class_probabilities = {
                CLASS_NAMES[i]: float(predictions[0][i])
                for i in range(len(CLASS_NAMES))
            }
            
        elif model_type == 'pytorch':
            import torch
            
            with torch.no_grad():
                outputs = model(processed_image)
                
                # Apply softmax to get probabilities
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                predicted_class_idx = torch.argmax(probabilities, dim=1).item()
                confidence = float(probabilities[0][predicted_class_idx])
                
                # Get all class probabilities
                class_probabilities = {
                    CLASS_NAMES[i]: float(probabilities[0][i])
                    for i in range(len(CLASS_NAMES))
                }
        
        predicted_class = CLASS_NAMES[predicted_class_idx]
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        # Upload to Supabase Storage and save to database
        if db is not None:
            try:
                # Upload image to Supabase Storage
                db.upload_image(image_bytes, unique_filename)
                print(f"Image uploaded to Supabase Storage: {unique_filename}")
                
                # Save prediction to database (without image_url)
                db.save_prediction(unique_filename, predicted_class, confidence)
                
                # Get image URL from filename
                image_url = db.get_image_url(unique_filename)
            except Exception as e:
                print(f"Warning: Could not save to Supabase: {e}")
                # Fallback to local storage if Supabase fails
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                image_url = None
        else:
            # Save to local storage if database not connected
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            image_url = None
        
        # Return response
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': class_probabilities,
            'image_url': image_url,  # Include Supabase Storage URL constructed from filename
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
        
        # Add image URLs for each prediction using the filename
        for prediction in predictions:
            if 'filename' in prediction:
                prediction['image_url'] = db.get_image_url(prediction['filename'])
        
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
