"""
Download and prepare dataset for Robot vs Human classification
This script downloads images and organizes them into train/val/test splits
"""
import os
import sys
import requests
from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RAW_DATA_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR


def create_directory_structure():
    """Create the directory structure for the dataset"""
    directories = [
        RAW_DATA_DIR / "human",
        RAW_DATA_DIR / "robot",
        TRAIN_DIR / "human",
        TRAIN_DIR / "robot",
        VAL_DIR / "human",
        VAL_DIR / "robot",
        TEST_DIR / "human",
        TEST_DIR / "robot",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✓ Directory structure created successfully!")


def download_sample_images():
    """
    Download sample images for demonstration
    Note: For a real dataset, you should use a proper source like:
    - Kaggle datasets
    - ImageNet
    - Custom scraped images
    """
    print("\n" + "="*60)
    print("DATASET PREPARATION INSTRUCTIONS")
    print("="*60)
    print("\nThis script has created the directory structure.")
    print("You need to populate it with images:\n")
    print(f"1. Place human images in: {RAW_DATA_DIR / 'human'}")
    print(f"2. Place robot images in: {RAW_DATA_DIR / 'robot'}")
    print("\nRecommended sources:")
    print("- Kaggle: Search for 'robot vs human' or similar datasets")
    print("- Google Images: Use bulk downloaders with proper licenses")
    print("- Custom collection: Gather your own images")
    print("\nMinimum recommended: 200+ images per class")
    print("After adding images, run this script again to split them.")
    print("="*60 + "\n")


def split_dataset(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    """
    Split images from raw directory into train/val/test sets
    
    Args:
        train_ratio: Proportion for training set
        val_ratio: Proportion for validation set
        test_ratio: Proportion for test set
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.01, "Ratios must sum to 1"
    
    for class_name in ['human', 'robot']:
        raw_class_dir = RAW_DATA_DIR / class_name
        
        # Get all image files
        image_files = [f for f in raw_class_dir.glob('*') 
                      if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']]
        
        if len(image_files) == 0:
            print(f"⚠ No images found for class '{class_name}' in {raw_class_dir}")
            continue
        
        print(f"\nProcessing {len(image_files)} images for class '{class_name}'...")
        
        # Shuffle
        random.shuffle(image_files)
        
        # Calculate split points
        n_train = int(len(image_files) * train_ratio)
        n_val = int(len(image_files) * val_ratio)
        
        train_files = image_files[:n_train]
        val_files = image_files[n_train:n_train + n_val]
        test_files = image_files[n_train + n_val:]
        
        # Copy files to appropriate directories
        for file_list, target_dir in [
            (train_files, TRAIN_DIR / class_name),
            (val_files, VAL_DIR / class_name),
            (test_files, TEST_DIR / class_name)
        ]:
            for img_file in file_list:
                shutil.copy2(img_file, target_dir / img_file.name)
        
        print(f"  ✓ Train: {len(train_files)} images")
        print(f"  ✓ Validation: {len(val_files)} images")
        print(f"  ✓ Test: {len(test_files)} images")


def verify_dataset():
    """Verify the dataset structure and count images"""
    print("\n" + "="*60)
    print("DATASET VERIFICATION")
    print("="*60)
    
    total_train = 0
    total_val = 0
    total_test = 0
    
    for split_name, split_dir in [('Train', TRAIN_DIR), ('Validation', VAL_DIR), ('Test', TEST_DIR)]:
        print(f"\n{split_name} Set:")
        for class_name in ['human', 'robot']:
            class_dir = split_dir / class_name
            n_images = len(list(class_dir.glob('*')))
            print(f"  {class_name}: {n_images} images")
            
            if split_name == 'Train':
                total_train += n_images
            elif split_name == 'Validation':
                total_val += n_images
            else:
                total_test += n_images
    
    print(f"\nTotal images:")
    print(f"  Train: {total_train}")
    print(f"  Validation: {total_val}")
    print(f"  Test: {total_test}")
    print(f"  Grand Total: {total_train + total_val + total_test}")
    
    if total_train + total_val + total_test == 0:
        print("\n⚠ WARNING: No images found! Please add images to the raw directory first.")
        return False
    elif total_train < 50:
        print("\n⚠ WARNING: Very few training images. Model performance may be poor.")
        print("  Recommended: 200+ images per class")
    else:
        print("\n✓ Dataset looks good!")
    
    print("="*60 + "\n")
    return True


def main():
    """Main function to prepare the dataset"""
    print("Starting dataset preparation...\n")
    
    # Create directory structure
    create_directory_structure()
    
    # Check if raw data exists
    human_images = list((RAW_DATA_DIR / "human").glob('*'))
    robot_images = list((RAW_DATA_DIR / "robot").glob('*'))
    
    if len(human_images) == 0 or len(robot_images) == 0:
        download_sample_images()
        print("\n⚠ Please add images to the raw directory and run this script again.")
        return
    
    # Split dataset
    print("\nSplitting dataset into train/val/test...")
    split_dataset(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    
    # Verify
    verify_dataset()
    
    print("\n✓ Dataset preparation complete!")
    print("You can now proceed to train the model using train.py")


if __name__ == "__main__":
    main()
