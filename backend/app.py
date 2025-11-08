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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import (
    MODEL_PATH,
    MODEL_TYPE,
    MODEL_INPUT_SIZE,
    CLASS_NAMES,
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH,
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG,
    MODEL_BACKBONE,
    PREDICTION_THRESHOLD,
    PREDICTION_MARGIN,
)
from backend.supabase_db import SupabaseDB

app = Flask(__name__, static_folder='../frontend', static_url_path='')

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "ngrok-skip-browser-warning"]
    }
})

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,ngrok-skip-browser-warning')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

model = None
model_type = None  # 'keras' or 'pytorch'
db = None


def analyze_probabilities(probabilities):
    """
    Apply thresholding logic to convert raw probabilities into a prediction.
    """
    sorted_indices = np.argsort(probabilities)[::-1]
    top_idx = sorted_indices[0]
    top_conf = float(probabilities[top_idx])
    second_idx = sorted_indices[1] if len(sorted_indices) > 1 else top_idx
    second_conf = float(probabilities[second_idx]) if len(sorted_indices) > 1 else 0.0

    margin = top_conf - second_conf
    is_confident = (top_conf >= PREDICTION_THRESHOLD) and (margin >= PREDICTION_MARGIN)
    predicted_label = CLASS_NAMES[top_idx] if is_confident else "unknown"

    return {
        "predicted_label": predicted_label,
        "confidence": top_conf,
        "best_class": CLASS_NAMES[top_idx],
        "best_confidence": top_conf,
        "second_class": CLASS_NAMES[second_idx] if len(sorted_indices) > 1 else None,
        "second_confidence": second_conf,
        "margin": margin,
        "is_confident": is_confident,
    }

def load_model():
    """Load the trained model (supports both Keras and PyTorch)"""
    global model, model_type
    
    try:
        if not MODEL_PATH.exists():
            print(f"⚠ WARNING: Model file not found at {MODEL_PATH}")
            print("Please train the model first using train.py")
            return False
        
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
            
            model = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
            
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
    image = Image.open(io.BytesIO(image_bytes))
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    image = image.resize(MODEL_INPUT_SIZE)
    
    if model_type == 'keras':
        image_array = np.array(image).astype(np.float32)
        image_array = np.expand_dims(image_array, axis=0)

        if MODEL_BACKBONE.lower().startswith("efficientnet"):
            from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess_input

            image_array = efficientnet_preprocess_input(image_array)
        else:
            image_array /= 255.0
        return image_array
        
    elif model_type == 'pytorch':
        import torch
        from torchvision import transforms
        
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
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.'
        }), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        if model_type == 'keras':
            predictions = model.predict(processed_image, verbose=0)
            probabilities = predictions[0]
        elif model_type == 'pytorch':
            import torch
            
            with torch.no_grad():
                outputs = model(processed_image)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0].cpu().numpy()
        else:
            return jsonify({'error': 'Unsupported model type'}), 500

        analysis = analyze_probabilities(probabilities)
        class_probabilities = {
            CLASS_NAMES[i]: float(probabilities[i])
            for i in range(len(CLASS_NAMES))
        }
        
        predicted_class = analysis['predicted_label']
        confidence = analysis['confidence']
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        if db is not None:
            try:
                db.upload_image(image_bytes, unique_filename)
                print(f"Image uploaded to Supabase Storage: {unique_filename}")
                
                db.save_prediction(unique_filename, predicted_class, confidence)
                
                image_url = db.get_image_url(unique_filename)
            except Exception as e:
                print(f"Warning: Could not save to Supabase: {e}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                image_url = None
        else:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            image_url = None
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': class_probabilities,
            'decision_details': analysis,
            'image_url': image_url,  # Include Supabase Storage URL constructed from filename
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({
            'error': f'Prediction failed: {str(e)}'
        }), 500


@app.route('/api/predict-live', methods=['POST'])
def predict_live():
    """
    Predict image class for live feed (no database save, faster response)
    
    Expected: multipart/form-data with 'image' field
    Returns: JSON with predicted class and confidence
    """
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.'
        }), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        if model_type == 'keras':
            predictions = model.predict(processed_image, verbose=0)
            probabilities = predictions[0]
        elif model_type == 'pytorch':
            import torch
            
            with torch.no_grad():
                outputs = model(processed_image)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0].cpu().numpy()
        else:
            return jsonify({'error': 'Unsupported model type'}), 500

        analysis = analyze_probabilities(probabilities)
        class_probabilities = {
            CLASS_NAMES[i]: float(probabilities[i])
            for i in range(len(CLASS_NAMES))
        }
        
        predicted_class = analysis['predicted_label']
        confidence = analysis['confidence']
        
        return jsonify({
            'success': True,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': class_probabilities,
            'decision_details': analysis,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error during live prediction: {e}")
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
    
    model_loaded = load_model()
    if not model_loaded:
        print("\n⚠ WARNING: Starting server without model!")
        print("Train the model first: python model/train.py")
    
    db_connected = initialize_database()
    if not db_connected:
        print("\n⚠ WARNING: Starting server without database connection!")
    
    print("\n" + "="*60)
    print(f"Starting Flask server on http://{FLASK_HOST}:{FLASK_PORT}")
    print("="*60)
    print("\nAvailable endpoints:")
    print("  GET  /                    - Main web interface")
    print("  GET  /health              - Health check")
    print("  POST /api/predict         - Make prediction")
    print("  POST /api/predict-live    - Make live feed prediction (no DB save)")
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
