"""
Utility for Supabase database operations
"""
from supabase import create_client, Client
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE


class SupabaseDB:
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def save_prediction(self, filename: str, predicted_class: str, confidence: float) -> dict:
        """
        Save a prediction to the database
        
        Args:
            filename: Name of the uploaded image file
            predicted_class: The predicted class (human or robot)
            confidence: Confidence score of the prediction (0-1)
            
        Returns:
            Dictionary with the inserted data
        """
        try:
            data = {
                "filename": filename,
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.client.table(SUPABASE_TABLE).insert(data).execute()
            print(f"✓ Prediction saved to database: {filename} -> {predicted_class} ({confidence:.2%})")
            return response.data[0] if response.data else data
            
        except Exception as e:
            print(f"Error saving prediction to database: {e}")
            raise
    
    def get_all_predictions(self, limit: int = 100) -> list:
        """
        Retrieve all predictions from the database
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of prediction records
        """
        try:
            response = self.client.table(SUPABASE_TABLE)\
                .select("*")\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error retrieving predictions: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """
        Get statistics about predictions
        
        Returns:
            Dictionary with statistics
        """
        try:
            all_predictions = self.get_all_predictions(limit=1000)
            
            if not all_predictions:
                return {
                    "total": 0,
                    "humans": 0,
                    "robots": 0,
                    "avg_confidence": 0
                }
            
            humans = sum(1 for p in all_predictions if p['predicted_class'] == 'human')
            robots = sum(1 for p in all_predictions if p['predicted_class'] == 'robot')
            avg_conf = sum(p['confidence'] for p in all_predictions) / len(all_predictions)
            
            return {
                "total": len(all_predictions),
                "humans": humans,
                "robots": robots,
                "avg_confidence": avg_conf
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}


if __name__ == "__main__":
    # Test the connection
    db = SupabaseDB()
    print("✓ Supabase connection successful!")
    
    # Test saving a prediction
    test_result = db.save_prediction(
        filename="test_image.jpg",
        predicted_class="robot",
        confidence=0.95
    )
    print(f"Test prediction saved: {test_result}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Database statistics: {stats}")
