"""
Example usage scripts for the Robot vs Human Classifier API
"""
import requests
import json
from pathlib import Path

# API Configuration
API_BASE_URL = "https://xenia-unsmotherable-colette.ngrok-free.dev/"

def test_health():
    """Test if the API is running"""
    print("\n" + "="*60)
    print("Testing API Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        data = response.json()
        
        print(f"Status: {data['status']}")
        print(f"Model Loaded: {data['model_loaded']}")
        print(f"Database Connected: {data['database_connected']}")
        print(f"Timestamp: {data['timestamp']}")
        
        if data['status'] == 'healthy':
            print("\n✓ API is healthy and ready!")
            return True
        else:
            print("\n✗ API health check failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Error connecting to API: {e}")
        print("Make sure the server is running: python backend/app.py")
        return False


def predict_image(image_path):
    """
    Make a prediction for a single image
    
    Args:
        image_path: Path to the image file
    """
    print("\n" + "="*60)
    print(f"Predicting: {image_path}")
    print("="*60)
    
    if not Path(image_path).exists():
        print(f"✗ Image not found: {image_path}")
        return None
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_BASE_URL}/api/predict", files=files)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✓ Prediction successful!")
            print(f"  Class: {data['predicted_class'].upper()}")
            print(f"  Confidence: {data['confidence']:.2%}")
            print(f"  Filename: {data['filename']}")
            print(f"  Timestamp: {data['timestamp']}")
            
            print(f"\n  All Probabilities:")
            for cls, prob in data['all_probabilities'].items():
                print(f"    {cls}: {prob:.2%}")
            
            return data
        else:
            error_data = response.json()
            print(f"\n✗ Prediction failed: {error_data.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"\n✗ Error making prediction: {e}")
        return None


def batch_predict(image_folder):
    """
    Make predictions for all images in a folder
    
    Args:
        image_folder: Path to folder containing images
    """
    print("\n" + "="*60)
    print(f"Batch Prediction from: {image_folder}")
    print("="*60)
    
    folder = Path(image_folder)
    if not folder.exists():
        print(f"✗ Folder not found: {image_folder}")
        return
    
    # Find all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    images = [f for f in folder.iterdir() 
              if f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"✗ No images found in {image_folder}")
        return
    
    print(f"\nFound {len(images)} images")
    print("\nProcessing...")
    
    results = []
    for img in images:
        result = predict_image(str(img))
        if result:
            results.append({
                'filename': img.name,
                'class': result['predicted_class'],
                'confidence': result['confidence']
            })
    
    # Summary
    print("\n" + "="*60)
    print("BATCH PREDICTION SUMMARY")
    print("="*60)
    print(f"\nTotal images: {len(images)}")
    print(f"Successful predictions: {len(results)}")
    
    if results:
        humans = sum(1 for r in results if r['class'] == 'human')
        robots = sum(1 for r in results if r['class'] == 'robot')
        avg_conf = sum(r['confidence'] for r in results) / len(results)
        
        print(f"\nResults:")
        print(f"  Humans: {humans}")
        print(f"  Robots: {robots}")
        print(f"  Average Confidence: {avg_conf:.2%}")


def get_history(limit=10):
    """Get prediction history"""
    print("\n" + "="*60)
    print(f"Getting last {limit} predictions")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/history?limit={limit}")
        data = response.json()
        
        if data['success']:
            predictions = data['predictions']
            
            if not predictions:
                print("\nNo predictions found in database")
                return
            
            print(f"\nFound {len(predictions)} predictions:\n")
            
            for i, pred in enumerate(predictions, 1):
                emoji = "👤" if pred['predicted_class'] == 'human' else "🤖"
                print(f"{i}. {emoji} {pred['predicted_class'].upper()}")
                print(f"   File: {pred['filename']}")
                print(f"   Confidence: {pred['confidence']:.2%}")
                print(f"   Time: {pred['timestamp']}")
                print()
        else:
            print(f"✗ Failed to get history: {data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Error getting history: {e}")


def get_statistics():
    """Get prediction statistics"""
    print("\n" + "="*60)
    print("Getting Statistics")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/statistics")
        data = response.json()
        
        if data['success']:
            stats = data['statistics']
            
            print(f"\nTotal Predictions: {stats['total']}")
            print(f"Humans: {stats['humans']}")
            print(f"Robots: {stats['robots']}")
            print(f"Average Confidence: {stats['avg_confidence']:.2%}")
            
            if stats['total'] > 0:
                human_pct = (stats['humans'] / stats['total']) * 100
                robot_pct = (stats['robots'] / stats['total']) * 100
                print(f"\nDistribution:")
                print(f"  👤 Humans: {human_pct:.1f}%")
                print(f"  🤖 Robots: {robot_pct:.1f}%")
        else:
            print(f"✗ Failed to get statistics: {data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Error getting statistics: {e}")


def get_model_info():
    """Get model information"""
    print("\n" + "="*60)
    print("Getting Model Information")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/model-info")
        data = response.json()
        
        if data['success']:
            print(f"\nModel Path: {data['model_path']}")
            print(f"Input Size: {data['input_size']}")
            print(f"Classes: {', '.join(data['classes'])}")
            print(f"Number of Classes: {data['num_classes']}")
            print(f"Total Parameters: {data['total_parameters']:,}")
        else:
            print(f"✗ Failed to get model info: {data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Error getting model info: {e}")


def main():
    """Main example usage"""
    print("\n" + "="*60)
    print("ROBOT VS HUMAN CLASSIFIER - API EXAMPLES")
    print("="*60)
    
    # Test health first
    if not test_health():
        return
    
    # Get model info
    get_model_info()
    
    # Get statistics
    get_statistics()
    
    # Get history
    get_history(limit=5)
    
    # Example predictions (uncomment and add your image paths)
    print("\n" + "="*60)
    print("Example Predictions")
    print("="*60)
    print("\nTo make predictions, uncomment and modify:")
    print("  predict_image('path/to/your/image.jpg')")
    print("  batch_predict('path/to/image/folder')")
    
    # Uncomment these lines and add your image paths:
    # predict_image('data/test/human/image1.jpg')
    # predict_image('data/test/robot/image2.jpg')
    # batch_predict('data/test/human')
    
    print("\n" + "="*60)
    print("✓ Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
