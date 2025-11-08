# PyTorch Model Support

## Overview
The application now supports both **Keras (.h5)** and **PyTorch (.pth/.pt)** models for image classification.

## Quick Start

### 1. Install PyTorch Dependencies
```bash
pip install torch torchvision
```

Or update all dependencies:
```bash
pip install -r backend/requirements.txt
```

### 2. Place Your PyTorch Model
Copy your `.pth` or `.pt` model file to the model directory:
```
model/robot_vs_human_classifier.pth
```

### 3. Update Configuration
Edit `backend/config.py`:
```python
MODEL_PATH = MODEL_DIR / "robot_vs_human_classifier.pth"  # Change extension
MODEL_TYPE = "auto"  # Will auto-detect from extension
```

### 4. Run the Application
```bash
python backend/app.py
```

The app will automatically detect and load your PyTorch model!

## Model Requirements

### PyTorch Model Format
Your `.pth` file should contain the complete model (not just state_dict):

**Correct way to save:**
```python
import torch

# Save complete model
torch.save(model, 'robot_vs_human_classifier.pth')
```

**If you only have state_dict:**
```python
# You need to define your model architecture first
class YourModelArchitecture(nn.Module):
    # Your model definition here
    pass

model = YourModelArchitecture()
model.load_state_dict(torch.load('state_dict.pth'))
torch.save(model, 'robot_vs_human_classifier.pth')
```

### Model Output Requirements
- **Input**: RGB images of size (224, 224) - configurable in config.py
- **Output**: 2 class logits (human, robot)
- Model should accept input shape: `(batch_size, 3, 224, 224)`

## Model Architecture Example

### Simple CNN for PyTorch
```python
import torch
import torch.nn as nn

class RobotHumanClassifier(nn.Module):
    def __init__(self):
        super(RobotHumanClassifier, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 28 * 28, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 2)  # 2 classes: human, robot
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Create and save model
model = RobotHumanClassifier()
# ... train your model ...
torch.save(model, 'model/robot_vs_human_classifier.pth')
```

## Preprocessing Differences

### Keras (TensorFlow)
- Input shape: `(batch, height, width, channels)` - **BHWC**
- Normalization: `[0, 1]` range (divide by 255)
- Channel order: RGB

### PyTorch
- Input shape: `(batch, channels, height, width)` - **BCHW**
- Normalization: ImageNet stats
  - Mean: `[0.485, 0.456, 0.406]`
  - Std: `[0.229, 0.224, 0.225]`
- Channel order: RGB

The app handles these differences automatically!

## Configuration Options

### config.py Settings
```python
# Model configuration
MODEL_PATH = MODEL_DIR / "robot_vs_human_classifier.pth"
MODEL_TYPE = "auto"  # Options: "auto", "keras", "pytorch"
MODEL_INPUT_SIZE = (224, 224)
NUM_CLASSES = 2
CLASS_NAMES = ['human', 'robot']
```

### Model Type Detection
- **"auto"**: Detects from file extension
  - `.h5`, `.keras` → Keras
  - `.pth`, `.pt` → PyTorch
- **"keras"**: Force Keras loading
- **"pytorch"**: Force PyTorch loading

## Using Pre-trained Models

### Transfer Learning Example (PyTorch)
```python
import torch
import torchvision.models as models

# Use ResNet18 as base
model = models.resnet18(pretrained=True)

# Replace final layer for binary classification
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 2)

# Train your model...
# ... training code ...

# Save complete model
torch.save(model, 'model/robot_vs_human_classifier.pth')
```

### Popular Architectures
- **ResNet18/34/50** - Good balance of speed and accuracy
- **MobileNetV2** - Fast, mobile-optimized
- **EfficientNet** - State-of-the-art accuracy
- **VGG16** - Simple, proven architecture

## API Behavior

### Prediction Response (Same for Both)
```json
{
  "success": true,
  "filename": "20251108_143025_image.jpg",
  "predicted_class": "robot",
  "confidence": 0.9234,
  "all_probabilities": {
    "human": 0.0766,
    "robot": 0.9234
  },
  "image_url": "https://...",
  "timestamp": "2025-11-08T14:30:25"
}
```

## Troubleshooting

### Error: "Import torch could not be resolved"
**Solution:** Install PyTorch
```bash
pip install torch torchvision
```

### Error: "Loaded state_dict. You need to define the model architecture"
**Solution:** Your `.pth` file contains only weights, not the model.
1. Define your model architecture in code
2. Load the state dict into it
3. Save the complete model

### Error: "Model prediction failed"
**Causes:**
- Input size mismatch (check MODEL_INPUT_SIZE)
- Wrong number of output classes
- Model expects different preprocessing

**Solution:** Check your model's expected input/output format

### Performance Issues
**PyTorch CPU Mode:**
- Models run on CPU by default
- For GPU: Install CUDA-enabled PyTorch
- Check: `torch.cuda.is_available()`

## Switching Between Models

### From Keras to PyTorch
1. Update MODEL_PATH to `.pth` file
2. Set MODEL_TYPE = "auto" or "pytorch"
3. Restart server

### From PyTorch to Keras
1. Update MODEL_PATH to `.h5` file
2. Set MODEL_TYPE = "auto" or "keras"
3. Restart server

## Best Practices

1. **Model Saving**: Always save complete model, not just state_dict
2. **Input Size**: Match MODEL_INPUT_SIZE to your model's training size
3. **Class Order**: Ensure CLASS_NAMES matches your model's output order
4. **Testing**: Test predictions after switching models
5. **Version Control**: Don't commit large model files to git

## Example Training Script (PyTorch)

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Define transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load dataset
train_dataset = datasets.ImageFolder('data/train', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Create model
model = RobotHumanClassifier()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(10):
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

# Save model
torch.save(model, 'model/robot_vs_human_classifier.pth')
print("Model saved!")
```

## Additional Resources

- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [TorchVision Models](https://pytorch.org/vision/stable/models.html)
- [Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
