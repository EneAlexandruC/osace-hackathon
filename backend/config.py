"""
Configuration file for the CNN Image Classification project
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SUPABASE_URL = "https://sjfmoxyekzlkmkcrglyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNqZm1veHlla3psa21rY3JnbHl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1NzExMDAsImV4cCI6MjA3ODE0NzEwMH0.JDhaxBPjiCNsTR7R00X0AbVX7wlXJJ7PgCiubjuu-iw"
SUPABASE_TABLE = "classification"
SUPABASE_BUCKET = "classification-images"

MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "robot_vs_human_classifier.h5"  # Can be .h5 or .pth
MODEL_TYPE = "auto"  # auto, keras, or pytorch
MODEL_BACKBONE = os.environ.get("MODEL_BACKBONE", "efficientnet_b0").lower()

CLASS_NAMES = ['human', 'robot']
NUM_CLASSES = len(CLASS_NAMES)

EFFICIENTNET_INPUT_SIZES = {
    "efficientnet_b0": (224, 224),
    "efficientnet_b1": (240, 240),
    "efficientnet_b2": (260, 260),
    "efficientnet_b3": (300, 300),
}

MODEL_INPUT_SIZE = EFFICIENTNET_INPUT_SIZES.get(MODEL_BACKBONE, (224, 224))

DATA_DIR = BASE_DIR / "data"
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
TEST_DIR = DATA_DIR / "test"
RAW_DATA_DIR = DATA_DIR / "raw"

BATCH_SIZE = 32
EPOCHS = 15
LEARNING_RATE = 5e-4
VALIDATION_SPLIT = 0.2
USE_FINE_TUNING = True
FINE_TUNE_AT = -50  # Unfreeze the last 50 layers of the EfficientNet backbone
FINE_TUNE_EPOCHS = 10
FINE_TUNE_LEARNING_RATE = 1e-5
PREDICTION_THRESHOLD = 0.6  # Minimum confidence required to report a class
PREDICTION_MARGIN = 0.15  # Minimum gap between top-2 classes to be confident
UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

for directory in [MODEL_DIR, DATA_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR, 
                  RAW_DATA_DIR, UPLOAD_FOLDER]:
    directory.mkdir(parents=True, exist_ok=True)
