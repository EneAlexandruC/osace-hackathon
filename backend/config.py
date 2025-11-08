"""
Configuration file for the CNN Image Classification project
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Supabase configuration
SUPABASE_URL = "https://sjfmoxyekzlkmkcrglyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNqZm1veHlla3psa21rY3JnbHl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1NzExMDAsImV4cCI6MjA3ODE0NzEwMH0.JDhaxBPjiCNsTR7R00X0AbVX7wlXJJ7PgCiubjuu-iw"
SUPABASE_TABLE = "predictions"

# Model configuration
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "robot_vs_human_classifier.h5"
MODEL_INPUT_SIZE = (224, 224)  # Image size for the model
NUM_CLASSES = 2  # robots vs humans

# Data directories
DATA_DIR = BASE_DIR / "data"
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
TEST_DIR = DATA_DIR / "test"
RAW_DATA_DIR = DATA_DIR / "raw"

# Training configuration
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2

# Class names
CLASS_NAMES = ['human', 'robot']

# Upload configuration
UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Flask configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Create necessary directories
for directory in [MODEL_DIR, DATA_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR, 
                  RAW_DATA_DIR, UPLOAD_FOLDER]:
    directory.mkdir(parents=True, exist_ok=True)
