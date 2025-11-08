"""
Training script for Robot vs Human CNN Classifier
"""
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import (
    TRAIN_DIR, VAL_DIR, TEST_DIR, MODEL_PATH, MODEL_INPUT_SIZE,
    BATCH_SIZE, EPOCHS, LEARNING_RATE, CLASS_NAMES
)
from model.cnn_model import create_model, get_data_augmentation, get_preprocessing_layers


def create_datasets():
    """
    Create training, validation, and test datasets from directories
    
    Returns:
        Tuple of (train_ds, val_ds, test_ds)
    """
    print("Loading datasets...")
    
    # Training dataset with augmentation
    train_ds = keras.preprocessing.image_dataset_from_directory(
        TRAIN_DIR,
        labels='inferred',
        label_mode='categorical',
        class_names=CLASS_NAMES,
        batch_size=BATCH_SIZE,
        image_size=MODEL_INPUT_SIZE,
        shuffle=True,
        seed=42
    )
    
    # Validation dataset (no augmentation)
    val_ds = keras.preprocessing.image_dataset_from_directory(
        VAL_DIR,
        labels='inferred',
        label_mode='categorical',
        class_names=CLASS_NAMES,
        batch_size=BATCH_SIZE,
        image_size=MODEL_INPUT_SIZE,
        shuffle=False,
        seed=42
    )
    
    # Test dataset (no augmentation)
    test_ds = keras.preprocessing.image_dataset_from_directory(
        TEST_DIR,
        labels='inferred',
        label_mode='categorical',
        class_names=CLASS_NAMES,
        batch_size=BATCH_SIZE,
        image_size=MODEL_INPUT_SIZE,
        shuffle=False,
        seed=42
    )
    
    # Apply preprocessing and augmentation
    preprocessing = get_preprocessing_layers()
    augmentation = get_data_augmentation()
    
    # Apply to training data
    train_ds = train_ds.map(lambda x, y: (preprocessing(augmentation(x)), y))
    
    # Apply only preprocessing to val and test
    val_ds = val_ds.map(lambda x, y: (preprocessing(x), y))
    test_ds = test_ds.map(lambda x, y: (preprocessing(x), y))
    
    # Performance optimization
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    print(f"✓ Datasets loaded successfully!")
    print(f"  Training batches: {len(train_ds)}")
    print(f"  Validation batches: {len(val_ds)}")
    print(f"  Test batches: {len(test_ds)}")
    
    return train_ds, val_ds, test_ds


def create_callbacks(model_path):
    """
    Create training callbacks
    
    Args:
        model_path: Path to save the best model
        
    Returns:
        List of callbacks
    """
    callbacks = [
        # Save best model
        keras.callbacks.ModelCheckpoint(
            model_path,
            monitor='val_accuracy',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        
        # Early stopping
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        
        # Reduce learning rate on plateau
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        
        # TensorBoard logging
        keras.callbacks.TensorBoard(
            log_dir=f'logs/fit/{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            histogram_freq=1
        )
    ]
    
    return callbacks


def plot_training_history(history, save_path='training_history.png'):
    """
    Plot and save training history
    
    Args:
        history: Training history object
        save_path: Path to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Accuracy
    axes[0, 0].plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
    axes[0, 0].plot(history.history['val_accuracy'], label='Val Accuracy', linewidth=2)
    axes[0, 0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Loss
    axes[0, 1].plot(history.history['loss'], label='Train Loss', linewidth=2)
    axes[0, 1].plot(history.history['val_loss'], label='Val Loss', linewidth=2)
    axes[0, 1].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Precision
    if 'precision' in history.history:
        axes[1, 0].plot(history.history['precision'], label='Train Precision', linewidth=2)
        axes[1, 0].plot(history.history['val_precision'], label='Val Precision', linewidth=2)
        axes[1, 0].set_title('Model Precision', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # Recall
    if 'recall' in history.history:
        axes[1, 1].plot(history.history['recall'], label='Train Recall', linewidth=2)
        axes[1, 1].plot(history.history['val_recall'], label='Val Recall', linewidth=2)
        axes[1, 1].set_title('Model Recall', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Training history plot saved to: {save_path}")
    plt.close()


def evaluate_model(model, test_ds):
    """
    Evaluate model on test dataset
    
    Args:
        model: Trained model
        test_ds: Test dataset
        
    Returns:
        Dictionary with evaluation metrics
    """
    print("\nEvaluating model on test set...")
    results = model.evaluate(test_ds, verbose=1)
    
    metrics = {
        'test_loss': float(results[0]),
        'test_accuracy': float(results[1]),
        'test_precision': float(results[2]) if len(results) > 2 else None,
        'test_recall': float(results[3]) if len(results) > 3 else None
    }
    
    print("\n" + "="*60)
    print("TEST SET RESULTS")
    print("="*60)
    print(f"Loss: {metrics['test_loss']:.4f}")
    print(f"Accuracy: {metrics['test_accuracy']:.4f} ({metrics['test_accuracy']*100:.2f}%)")
    if metrics['test_precision']:
        print(f"Precision: {metrics['test_precision']:.4f}")
    if metrics['test_recall']:
        print(f"Recall: {metrics['test_recall']:.4f}")
    print("="*60)
    
    return metrics


def save_training_report(history, test_metrics, save_path='training_report.json'):
    """
    Save training report as JSON
    
    Args:
        history: Training history
        test_metrics: Test evaluation metrics
        save_path: Path to save the report
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'epochs': EPOCHS,
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE,
            'input_size': list(MODEL_INPUT_SIZE),
            'classes': CLASS_NAMES
        },
        'training_history': {
            key: [float(val) for val in values]
            for key, values in history.history.items()
        },
        'test_metrics': test_metrics,
        'final_metrics': {
            'train_accuracy': float(history.history['accuracy'][-1]),
            'val_accuracy': float(history.history['val_accuracy'][-1]),
            'test_accuracy': test_metrics['test_accuracy']
        }
    }
    
    with open(save_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Training report saved to: {save_path}")


def main():
    """Main training function"""
    print("\n" + "="*60)
    print("ROBOT VS HUMAN CNN CLASSIFIER - TRAINING")
    print("="*60)
    
    # Check if data exists
    if not TRAIN_DIR.exists() or not list(TRAIN_DIR.glob('*/*')):
        print("\n⚠ ERROR: Training data not found!")
        print(f"Please run prepare_dataset.py first to set up the data.")
        print(f"Expected location: {TRAIN_DIR}")
        return
    
    # Create datasets
    train_ds, val_ds, test_ds = create_datasets()
    
    # Create model
    print("\n" + "="*60)
    model = create_model(model_type='transfer_learning', learning_rate=LEARNING_RATE)
    
    # Create callbacks
    callbacks = create_callbacks(str(MODEL_PATH))
    
    # Train model
    print("\n" + "="*60)
    print("STARTING TRAINING")
    print("="*60)
    print(f"Epochs: {EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Learning rate: {LEARNING_RATE}")
    print("="*60 + "\n")
    
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    # Plot training history
    plot_training_history(history, 'training_history.png')
    
    # Evaluate on test set
    test_metrics = evaluate_model(model, test_ds)
    
    # Save training report
    save_training_report(history, test_metrics, 'training_report.json')
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED!")
    print("="*60)
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Training history plot: training_history.png")
    print(f"Training report: training_report.json")
    print("="*60 + "\n")
    
    # Check if accuracy goal is met
    if test_metrics['test_accuracy'] >= 0.90:
        print("✓ SUCCESS: Achieved >90% accuracy!")
    else:
        print(f"⚠ Target accuracy (90%) not reached. Got {test_metrics['test_accuracy']*100:.2f}%")
        print("  Consider: More training data, more epochs, or model tuning")


if __name__ == "__main__":
    main()
