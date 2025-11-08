"""
Quick test script to verify the setup and model prediction
"""
import sys
import os

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

print("\n" + "="*60)
print("ROBOT VS HUMAN CLASSIFIER - SYSTEM TEST")
print("="*60 + "\n")

# Test 1: Check imports
print("[1/6] Testing imports...")
try:
    import tensorflow as tf
    import numpy as np
    from PIL import Image
    print(f"  ✓ TensorFlow {tf.__version__}")
    print(f"  ✓ NumPy {np.__version__}")
    print("  ✓ Pillow installed")
except ImportError as e:
    print(f"  ✗ Import error: {e}")
    print("  Run: pip install -r backend/requirements.txt")
    sys.exit(1)

# Test 2: Check configuration
print("\n[2/6] Checking configuration...")
try:
    from backend.config import MODEL_PATH, SUPABASE_URL, DATA_DIR
    print(f"  ✓ Config loaded")
    print(f"  ✓ Model path: {MODEL_PATH}")
    print(f"  ✓ Data directory: {DATA_DIR}")
    print(f"  ✓ Supabase URL: {SUPABASE_URL[:30]}...")
except Exception as e:
    print(f"  ✗ Config error: {e}")
    sys.exit(1)

# Test 3: Check Supabase connection
print("\n[3/6] Testing Supabase connection...")
try:
    from backend.supabase_db import SupabaseDB
    db = SupabaseDB()
    print("  ✓ Supabase client created")
    
    # Try to get statistics
    stats = db.get_statistics()
    print(f"  ✓ Database accessible")
    print(f"    Total predictions: {stats.get('total', 0)}")
except Exception as e:
    print(f"  ⚠ Warning: Database connection failed: {e}")
    print("    The app will work, but predictions won't be saved")

# Test 4: Check model file
print("\n[4/6] Checking model file...")
if MODEL_PATH.exists():
    print(f"  ✓ Model file found: {MODEL_PATH}")
    print(f"    Size: {MODEL_PATH.stat().st_size / (1024*1024):.2f} MB")
else:
    print(f"  ⚠ Model file not found at {MODEL_PATH}")
    print("    Run: python model/train.py to train the model")

# Test 5: Check data directories
print("\n[5/6] Checking dataset...")
try:
    from backend.config import TRAIN_DIR, VAL_DIR, TEST_DIR, RAW_DATA_DIR
    
    def count_images(directory):
        if not directory.exists():
            return 0
        count = 0
        for class_dir in directory.iterdir():
            if class_dir.is_dir():
                count += len(list(class_dir.glob('*')))
        return count
    
    raw_count = count_images(RAW_DATA_DIR)
    train_count = count_images(TRAIN_DIR)
    val_count = count_images(VAL_DIR)
    test_count = count_images(TEST_DIR)
    
    print(f"  Raw images: {raw_count}")
    print(f"  Train images: {train_count}")
    print(f"  Validation images: {val_count}")
    print(f"  Test images: {test_count}")
    
    if raw_count == 0 and train_count == 0:
        print("  ⚠ No images found!")
        print("    Add images to data/raw/human/ and data/raw/robot/")
        print("    Then run: python model/prepare_dataset.py")
    elif train_count == 0:
        print("  ⚠ Dataset not split yet")
        print("    Run: python model/prepare_dataset.py")
    else:
        print("  ✓ Dataset ready for training")
        
except Exception as e:
    print(f"  ⚠ Error checking dataset: {e}")

# Test 6: Test model loading (if exists)
print("\n[6/6] Testing model loading...")
if MODEL_PATH.exists():
    try:
        from tensorflow import keras
        model = keras.models.load_model(MODEL_PATH)
        print("  ✓ Model loaded successfully")
        print(f"    Input shape: {model.input_shape}")
        print(f"    Output shape: {model.output_shape}")
        print(f"    Parameters: {model.count_params():,}")
    except Exception as e:
        print(f"  ✗ Error loading model: {e}")
else:
    print("  ⚠ Skipped (model not trained yet)")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

if MODEL_PATH.exists() and train_count > 0:
    print("\n✓ System is ready to use!")
    print("\nTo start the server:")
    print("  python backend/app.py")
    print("\nThen open: http://localhost:5000")
elif train_count > 0:
    print("\n⚠ Almost ready!")
    print("\nNext steps:")
    print("  1. Train the model: python model/train.py")
    print("  2. Start server: python backend/app.py")
    print("  3. Open: http://localhost:5000")
else:
    print("\n⚠ Setup needed!")
    print("\nNext steps:")
    print("  1. Add images to data/raw/human/ and data/raw/robot/")
    print("  2. Prepare dataset: python model/prepare_dataset.py")
    print("  3. Train model: python model/train.py")
    print("  4. Start server: python backend/app.py")

print("\n" + "="*60 + "\n")
