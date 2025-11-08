"""
Utility for Supabase database operations
"""
from supabase import create_client, Client
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE, SUPABASE_BUCKET


class SupabaseDB:
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.bucket = SUPABASE_BUCKET
    
    def upload_image(self, file_bytes: bytes, filename: str) -> str:
        """
        Upload an image to Supabase Storage
        
        Args:
            file_bytes: The image file as bytes
            filename: Name to save the file as
            
        Returns:
            The public URL of the uploaded image
        """
        try:
            self.client.storage.from_(self.bucket).upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            
            public_url = self.client.storage.from_(self.bucket).get_public_url(filename)
            print(f"✓ Image uploaded to Supabase Storage: {filename}")
            return public_url
            
        except Exception as e:
            print(f"Error uploading image to storage: {e}")
            raise
    
    def get_image_url(self, filename: str) -> str:
        """
        Get the public URL for an image in storage
        
        Args:
            filename: Name of the file in storage
            
        Returns:
            The public URL of the image
        """
        try:
            return self.client.storage.from_(self.bucket).get_public_url(filename)
        except Exception as e:
            print(f"Error getting image URL: {e}")
            return ""
    
    def save_prediction(self, filename: str, predicted_class: str, confidence: float) -> dict:
        """
        Save a prediction to the database
        
        Args:
            filename: Name of the uploaded image file (used to construct Supabase Storage URL)
            predicted_class: The predicted class (human or robot)
            confidence: Confidence score of the prediction (0-1)
            
        Returns:
            Dictionary with the inserted data
        """
        try:
            data = {
                "filename": filename,
                "predicted_class": predicted_class,
                "confidence": float(confidence)
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
                .order("created_at", desc=True)\
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
    db = SupabaseDB()
    print("✓ Supabase connection successful!")
    
    test_result = db.save_prediction(
        filename="test_image.jpg",
        predicted_class="robot",
        confidence=0.95
    )
    print(f"Test prediction saved: {test_result}")
    
    stats = db.get_statistics()
    print(f"Database statistics: {stats}")
