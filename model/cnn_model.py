"""
CNN Model architecture for Robot vs Human classification
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import (
    EfficientNetB0,
    EfficientNetB1,
    EfficientNetB2,
    EfficientNetB3,
)
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess_input
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import (
    MODEL_INPUT_SIZE,
    NUM_CLASSES,
    CLASS_NAMES,
    MODEL_BACKBONE,
    FINE_TUNE_AT,
)


EFFICIENTNET_BACKBONES = {
    "efficientnet_b0": EfficientNetB0,
    "efficientnet_b1": EfficientNetB1,
    "efficientnet_b2": EfficientNetB2,
    "efficientnet_b3": EfficientNetB3,
}


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
        layers.Input(shape=input_shape),
        
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def create_transfer_learning_model(
    backbone="efficientnet_b0",
    input_shape=(224, 224, 3),
    num_classes=2,
    fine_tune_at=None,
):
    """
    Create a transfer learning model using EfficientNet backbones.

    Args:
        backbone: EfficientNet variant to use ('efficientnet_b0' ... 'efficientnet_b3')
        input_shape: Shape of input images (height, width, channels)
        num_classes: Number of output classes
        fine_tune_at: Index at which to start fine-tuning the backbone layers (None = freeze all)

    Returns:
        Keras Model ready for compilation.
    """
    backbone_key = backbone.lower()

    if backbone_key not in EFFICIENTNET_BACKBONES:
        raise ValueError(
            f"Unsupported EfficientNet backbone '{backbone}'. "
            f"Available options: {', '.join(EFFICIENTNET_BACKBONES.keys())}"
        )

    base_model_constructor = EFFICIENTNET_BACKBONES[backbone_key]
    base_model_kwargs = {
        "input_shape": input_shape,
        "include_top": False,
        "weights": "imagenet",
    }

    constructor = getattr(base_model_constructor, "__init__", base_model_constructor)

    try:
        from inspect import signature

        constructor_params = signature(constructor).parameters
    except (TypeError, ValueError):
        constructor_params = {}

    if "drop_connect_rate" in constructor_params:
        base_model_kwargs["drop_connect_rate"] = 0.2

    base_model = base_model_constructor(**base_model_kwargs)

    total_layers = len(base_model.layers)

    if fine_tune_at is None:
        base_model.trainable = False
        trainable_layers = 0
    else:
        if fine_tune_at < 0:
            unfreeze_from = max(total_layers + fine_tune_at, 0)
        else:
            unfreeze_from = min(fine_tune_at, total_layers)

        base_model.trainable = True
        for layer in base_model.layers[:unfreeze_from]:
            layer.trainable = False

        trainable_layers = total_layers - unfreeze_from

        print(
            f"Fine-tuning EfficientNet starting at layer {unfreeze_from} "
            f"({trainable_layers} trainable layers)."
        )
    if trainable_layers == 0:
        print("EfficientNet backbone frozen (no fine-tuning).")

    inputs = layers.Input(shape=input_shape)
    x = base_model(inputs, training=False if not base_model.trainable else None)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="post_bn")(x)
    x = layers.Dropout(0.4, name="post_dropout")(x)
    x = layers.Dense(256, activation='relu', name="dense_1")(x)
    x = layers.BatchNormalization(name="bn_1")(x)
    x = layers.Dropout(0.3, name="dropout_1")(x)
    outputs = layers.Dense(num_classes, activation='softmax', name="predictions")(x)

    model = keras.Model(inputs, outputs, name=f"{backbone_key}_classifier")
    model.base_model = base_model
    return model


def get_data_augmentation():
    """
    Create data augmentation layers
    
    Returns:
        Sequential model with augmentation layers
    """
    return keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.3),
        layers.RandomZoom(0.25),
        layers.RandomContrast(0.3),
        layers.RandomBrightness(factor=0.2),
    ])


def get_preprocessing_layers(backbone=None):
    """
    Create preprocessing layers for normalization
    
    Returns:
        Sequential model with preprocessing layers
    """
    backbone = (backbone or MODEL_BACKBONE or "").lower()

    if backbone.startswith("efficientnet"):
        return keras.Sequential(
            [
                layers.Lambda(
                    lambda x: efficientnet_preprocess_input(x),
                    name="efficientnet_preprocess",
                )
            ],
            name="preprocessing_layers",
        )

    return keras.Sequential(
        [layers.Rescaling(1.0 / 255, name="default_rescale")],
        name="preprocessing_layers",
    )


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


def create_model(
    model_type='transfer_learning',
    learning_rate=0.001,
    backbone=None,
    fine_tune_at=FINE_TUNE_AT,
):
    """
    Create and compile the complete model
    
    Args:
        model_type: Type of model to create ('custom' or 'transfer_learning')
        learning_rate: Learning rate for training
        backbone: Name of EfficientNet backbone to use
        fine_tune_at: Layer index at which to start fine-tuning (None to keep frozen)
        
    Returns:
        Compiled Keras model ready for training
    """
    input_shape = (*MODEL_INPUT_SIZE, 3)
    backbone = (backbone or MODEL_BACKBONE).lower()
    
    if model_type == 'custom':
        print("Creating custom CNN model...")
        model = create_custom_cnn(input_shape, NUM_CLASSES)
    else:
        print(f"Creating transfer learning model ({backbone})...")
        model = create_transfer_learning_model(
            backbone=backbone,
            input_shape=input_shape,
            num_classes=NUM_CLASSES,
            fine_tune_at=fine_tune_at,
        )
    
    model = compile_model(model, learning_rate)
    
    print("\nModel Summary:")
    print("="*60)
    model.summary()
    print("="*60)
    
    return model


if __name__ == "__main__":
    print("Testing model creation...\n")
    
    model_tl = create_model(model_type='transfer_learning', backbone=MODEL_BACKBONE)
    print(f"\n✓ Transfer learning model created successfully!")
    print(f"  Total parameters: {model_tl.count_params():,}")
    
    model_custom = create_model(model_type='custom')
    print(f"\n✓ Custom CNN model created successfully!")
    print(f"  Total parameters: {model_custom.count_params():,}")
