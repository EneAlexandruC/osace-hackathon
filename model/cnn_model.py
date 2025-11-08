"""
CNN Model architecture for Robot vs Human classification
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import MODEL_INPUT_SIZE, NUM_CLASSES, CLASS_NAMES


def create_custom_cnn(input_shape=(224, 224, 3), num_classes=2):
    """
    Create a custom CNN model from scratch
    
    Args:
        input_shape: Shape of input images (height, width, channels)
        num_classes: Number of output classes
        
    Returns:
        Compiled Keras model
    """
    model = models.Sequential([
        # Input layer
        layers.Input(shape=input_shape),
        
        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Third convolutional block
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Fourth convolutional block
        layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Flatten and dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Output layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def create_transfer_learning_model(input_shape=(224, 224, 3), num_classes=2):
    """
    Create a model using transfer learning with MobileNetV2
    This approach typically gives better results with less training time
    
    Args:
        input_shape: Shape of input images (height, width, channels)
        num_classes: Number of output classes
        
    Returns:
        Compiled Keras model
    """
    # Load pre-trained MobileNetV2 model without top layers
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze the base model layers (we'll fine-tune later if needed)
    base_model.trainable = False
    
    # Create new model on top
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def get_data_augmentation():
    """
    Create data augmentation layers
    
    Returns:
        Sequential model with augmentation layers
    """
    return keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
        layers.RandomContrast(0.2),
    ])


def get_preprocessing_layers():
    """
    Create preprocessing layers for normalization
    
    Returns:
        Sequential model with preprocessing layers
    """
    return keras.Sequential([
        layers.Rescaling(1./255)
    ])


def compile_model(model, learning_rate=0.001):
    """
    Compile the model with optimizer, loss, and metrics
    
    Args:
        model: Keras model to compile
        learning_rate: Learning rate for the optimizer
        
    Returns:
        Compiled model
    """
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=[
            'accuracy',
            keras.metrics.Precision(name='precision'),
            keras.metrics.Recall(name='recall')
        ]
    )
    
    return model


def create_model(model_type='transfer_learning', learning_rate=0.001):
    """
    Create and compile the complete model
    
    Args:
        model_type: Type of model to create ('custom' or 'transfer_learning')
        learning_rate: Learning rate for training
        
    Returns:
        Compiled Keras model ready for training
    """
    input_shape = (*MODEL_INPUT_SIZE, 3)
    
    if model_type == 'custom':
        print("Creating custom CNN model...")
        model = create_custom_cnn(input_shape, NUM_CLASSES)
    else:
        print("Creating transfer learning model (MobileNetV2)...")
        model = create_transfer_learning_model(input_shape, NUM_CLASSES)
    
    # Compile the model
    model = compile_model(model, learning_rate)
    
    # Print model summary
    print("\nModel Summary:")
    print("="*60)
    model.summary()
    print("="*60)
    
    return model


if __name__ == "__main__":
    # Test model creation
    print("Testing model creation...\n")
    
    # Create transfer learning model
    model_tl = create_model(model_type='transfer_learning')
    print(f"\n✓ Transfer learning model created successfully!")
    print(f"  Total parameters: {model_tl.count_params():,}")
    
    # Create custom model
    model_custom = create_model(model_type='custom')
    print(f"\n✓ Custom CNN model created successfully!")
    print(f"  Total parameters: {model_custom.count_params():,}")
