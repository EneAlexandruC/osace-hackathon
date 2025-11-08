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
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, UnidentifiedImageError
from sklearn.metrics import confusion_matrix, classification_report

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import (
    TRAIN_DIR,
    VAL_DIR,
    TEST_DIR,
    MODEL_PATH,
    MODEL_INPUT_SIZE,
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    CLASS_NAMES,
    MODEL_BACKBONE,
    USE_FINE_TUNING,
    FINE_TUNE_AT,
    FINE_TUNE_EPOCHS,
    FINE_TUNE_LEARNING_RATE,
)
from model.cnn_model import (
    create_model,
    get_data_augmentation,
    get_preprocessing_layers,
    compile_model,
)

VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}


def find_corrupt_images(directories):
    """
    Scan provided directories for images that Pillow cannot open.

    Args:
        directories: Iterable of directory paths to scan.

    Returns:
        List of tuples (path, error_message) for corrupt/unreadable images.
    """
    corrupt_files = []

    for directory in directories:
        directory = Path(directory)
        if not directory.exists():
            continue

        for file_path in directory.rglob('*'):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in VALID_IMAGE_EXTENSIONS:
                continue

            try:
                with Image.open(file_path) as img:
                    img.verify()
                with Image.open(file_path) as img:
                    img.load()
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                corrupt_files.append((file_path, str(exc)))

    return corrupt_files


def create_datasets():
    """
    Create training, validation, and test datasets from directories
    
    Returns:
        Tuple of (train_ds, val_ds, test_ds)
    """
    print("Loading datasets...")
    
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
    
    preprocessing = get_preprocessing_layers(MODEL_BACKBONE)
    augmentation = get_data_augmentation()
    
    train_ds = train_ds.map(lambda x, y: (preprocessing(augmentation(x)), y))
    
    val_ds = val_ds.map(lambda x, y: (preprocessing(x), y))
    test_ds = test_ds.map(lambda x, y: (preprocessing(x), y))
    
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
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
        keras.callbacks.ModelCheckpoint(
            model_path,
            monitor='val_accuracy',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        
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
    
    axes[0, 0].plot(history.history.get('accuracy', []), label='Train Accuracy', linewidth=2)
    axes[0, 0].plot(history.history.get('val_accuracy', []), label='Val Accuracy', linewidth=2)
    axes[0, 0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(history.history.get('loss', []), label='Train Loss', linewidth=2)
    axes[0, 1].plot(history.history.get('val_loss', []), label='Val Loss', linewidth=2)
    axes[0, 1].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    if 'precision' in history.history:
        axes[1, 0].plot(history.history['precision'], label='Train Precision', linewidth=2)
        axes[1, 0].plot(history.history.get('val_precision', []), label='Val Precision', linewidth=2)
        axes[1, 0].set_title('Model Precision', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    if 'recall' in history.history:
        axes[1, 1].plot(history.history['recall'], label='Train Recall', linewidth=2)
        axes[1, 1].plot(history.history.get('val_recall', []), label='Val Recall', linewidth=2)
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
            'classes': CLASS_NAMES,
            'use_fine_tuning': USE_FINE_TUNING,
            'fine_tune_at': FINE_TUNE_AT,
            'fine_tune_epochs': FINE_TUNE_EPOCHS,
            'fine_tune_learning_rate': FINE_TUNE_LEARNING_RATE,
        },
        'training_history': {
            key: [float(val) for val in values]
            for key, values in history.history.items()
        },
        'test_metrics': test_metrics,
        'final_metrics': {
            'train_accuracy': float(history.history.get('accuracy', [0])[-1]),
            'val_accuracy': float(history.history.get('val_accuracy', [0])[-1]),
            'test_accuracy': test_metrics['test_accuracy']
        }
    }
    
    with open(save_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Training report saved to: {save_path}")


def generate_evaluation_artifacts(model, test_ds, class_names, cm_path, report_path):
    """
    Generate confusion matrix plot and classification report.
    """
    print("\nGenerating evaluation artifacts...")
    y_true = []
    y_pred = []

    for batch_images, batch_labels in test_ds:
        preds = model.predict(batch_images, verbose=0)
        y_pred.extend(np.argmax(preds, axis=1))
        y_true.extend(np.argmax(batch_labels.numpy(), axis=1))

    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    tick_marks = np.arange(len(class_names))
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)
    ax.set_ylabel('True label')
    ax.set_xlabel('Predicted label')
    ax.set_title('Confusion Matrix')

    thresh = cm.max() / 2.0 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, format(cm[i, j], 'd'),
                ha='center', va='center',
                color='white' if cm[i, j] > thresh else 'black'
            )

    plt.tight_layout()
    plt.savefig(cm_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Confusion matrix saved to: {cm_path}")

    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        digits=4
    )
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"✓ Classification report saved to: {report_path}")


def main():
    """Main training function"""
    print("\n" + "="*60)
    print("ROBOT VS HUMAN CNN CLASSIFIER - TRAINING")
    print("="*60)
    
    if not TRAIN_DIR.exists() or not list(TRAIN_DIR.glob('*/*')):
        print("\n⚠ ERROR: Training data not found!")
        print(f"Please run prepare_dataset.py first to set up the data.")
        print(f"Expected location: {TRAIN_DIR}")
        return
    
    corrupt_images = find_corrupt_images([TRAIN_DIR, VAL_DIR, TEST_DIR])
    if corrupt_images:
        print("\n⚠ ERROR: Found unreadable image files:")
        for file_path, error in corrupt_images[:10]:
            print(f"  - {file_path}: {error}")
        if len(corrupt_images) > 10:
            print(f"  ...and {len(corrupt_images) - 10} more.")
        print("\nPlease remove or replace the corrupt files and rerun the training.")
        return

    train_ds, val_ds, test_ds = create_datasets()
    
    print("\n" + "="*60)
    model = create_model(
        model_type='transfer_learning',
        learning_rate=LEARNING_RATE,
        backbone=MODEL_BACKBONE,
    )
    
    callbacks = create_callbacks(str(MODEL_PATH))
    
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

    histories = [history]

    if USE_FINE_TUNING and hasattr(model, "base_model"):
        print("\n" + "="*60)
        print("STARTING FINE-TUNING")
        print("="*60)

        base_model = model.base_model
        total_layers = len(base_model.layers)

        if FINE_TUNE_AT is None:
            fine_tune_start = 0
        elif FINE_TUNE_AT < 0:
            fine_tune_start = max(0, total_layers + FINE_TUNE_AT)
        else:
            fine_tune_start = min(total_layers, FINE_TUNE_AT)

        for layer in base_model.layers[:fine_tune_start]:
            layer.trainable = False
        for layer in base_model.layers[fine_tune_start:]:
            layer.trainable = True

        print(f"✓ Unfroze layers from index {fine_tune_start} (total layers: {total_layers})")
        print(f"Fine-tuning for {FINE_TUNE_EPOCHS} epochs at lr={FINE_TUNE_LEARNING_RATE}")

        model = compile_model(model, FINE_TUNE_LEARNING_RATE)
        fine_tune_callbacks = create_callbacks(str(MODEL_PATH))

        fine_tune_history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=EPOCHS + FINE_TUNE_EPOCHS,
            initial_epoch=EPOCHS,
            callbacks=fine_tune_callbacks,
            verbose=1
        )

        histories.append(fine_tune_history)

    combined_history_dict = {}
    for hist in histories:
        for key, values in hist.history.items():
            combined_history_dict.setdefault(key, [])
            combined_history_dict[key].extend(values)

    combined_history = SimpleNamespace(history=combined_history_dict)

    plot_training_history(combined_history, 'training_history.png')

    test_metrics = evaluate_model(model, test_ds)

    generate_evaluation_artifacts(
        model,
        test_ds,
        CLASS_NAMES,
        cm_path='confusion_matrix.png',
        report_path='classification_report.txt'
    )

    save_training_report(combined_history, test_metrics, 'training_report.json')

    print("\n" + "="*60)
    print("TRAINING COMPLETED!")
    print("="*60)
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Training history plot: training_history.png")
    print(f"Confusion matrix: confusion_matrix.png")
    print(f"Classification report: classification_report.txt")
    print(f"Training report: training_report.json")
    print("="*60 + "\n")

    if test_metrics['test_accuracy'] >= 0.90:
        print("✓ SUCCESS: Achieved >90% accuracy!")
    else:
        print(f"⚠ Target accuracy (90%) not reached. Got {test_metrics['test_accuracy']*100:.2f}%")
        print("  Consider: More training data, more epochs, or model tuning")


if __name__ == "__main__":
    main()
