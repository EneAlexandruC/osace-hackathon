# Quick Start Guide - Robot vs Human Classifier

## 🚀 Setup Rapid (PowerShell)

```powershell
# Clonează/Descarcă proiectul
cd osace-hackathon

# Rulează setup automat
.\setup.ps1

# SAU manual:
pip install -r backend\requirements.txt
```

## 📦 Pregătire Date

```powershell
# Crează structura de directoare
python model\prepare_dataset.py

# Adaugă imagini în:
# - data\raw\human\  (imagini cu oameni)
# - data\raw\robot\  (imagini cu roboți)

# Split dataset în train/val/test
python model\prepare_dataset.py
```

## 🧠 Antrenare Model

```powershell
# Antrenează modelul (10 epoci)
python model\train.py

# Outputs:
# - model\robot_vs_human_classifier.h5
# - training_history.png
# - training_report.json
```

## 🌐 Pornire Server

```powershell
# Start Flask API
python backend\app.py

# Server pornește pe: http://localhost:5000
```

## 🧪 Test Sistem

```powershell
# Verifică configurația completă
python test_system.py

# Test Supabase
python backend\supabase_db.py

# Test model
python model\cnn_model.py
```

## 📊 Utilizare API

### cURL Examples

```powershell
# Health check
curl http://localhost:5000/health

# Upload și predicție
curl -X POST -F "image=@path\to\image.jpg" http://localhost:5000/api/predict

# Istoric
curl http://localhost:5000/api/history?limit=10

# Statistici
curl http://localhost:5000/api/statistics

# Info model
curl http://localhost:5000/api/model-info
```

### Python Example

```python
import requests

# Upload imagine pentru predicție
with open('test_image.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/api/predict', files=files)
    result = response.json()
    
print(f"Class: {result['predicted_class']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## 🗄️ Setup Supabase

1. Creează cont pe [supabase.com](https://supabase.com)
2. Creează proiect nou
3. Copiază URL și API Key
4. Actualizează `backend\config.py`
5. Rulează SQL din `supabase_setup.sql` în SQL Editor

## 📁 Structură Fișiere Importante

```
osace-hackathon/
├── backend/
│   ├── app.py              # 🌐 Flask server
│   ├── config.py           # ⚙️ Configurări
│   └── supabase_db.py      # 🗄️ Database client
├── model/
│   ├── train.py            # 🧠 Antrenare
│   ├── cnn_model.py        # 🏗️ Arhitectură
│   └── prepare_dataset.py  # 📦 Pregătire date
├── frontend/
│   └── index.html          # 🎨 Web UI
├── data/
│   └── raw/                # 📸 Imaginile tale aici!
└── test_system.py          # 🧪 Test complet
```

## 🎯 Workflow Complet

```powershell
# 1. Setup
pip install -r backend\requirements.txt

# 2. Adaugă imagini în data\raw\human\ și data\raw\robot\

# 3. Pregătește dataset
python model\prepare_dataset.py

# 4. Antrenează model
python model\train.py

# 5. Test sistem
python test_system.py

# 6. Pornește server
python backend\app.py

# 7. Deschide browser la http://localhost:5000
```

## 🔧 Troubleshooting Rapid

### Eroare: Module not found
```powershell
pip install -r backend\requirements.txt
```

### Eroare: Model not found
```powershell
python model\train.py
```

### Eroare: No images found
```powershell
# Adaugă imagini în data\raw\human\ și data\raw\robot\
python model\prepare_dataset.py
```

### Eroare: Supabase connection
- Verifică internet
- Confirmă API key în config.py
- Rulează supabase_setup.sql în Supabase

### Port 5000 deja folosit
```powershell
# Schimbă portul în backend\config.py
FLASK_PORT = 5001
```

## 📈 Verificare Performance

După antrenare, verifică:
- `training_history.png` - Grafice
- `training_report.json` - Metrici
- Terminal - Accuracy pe test set

**Obiectiv**: Accuracy > 90%

## 🎨 Customizare

### Schimbă numărul de epoci
```python
# În backend\config.py
EPOCHS = 20  # Crește pentru accuracy mai bună
```

### Schimbă learning rate
```python
# În backend\config.py
LEARNING_RATE = 0.0005  # Scade pentru stabilitate
```

### Folosește model custom în loc de transfer learning
```python
# În model\train.py, linia ~250
model = create_model(model_type='custom', learning_rate=LEARNING_RATE)
```

## 📞 Suport

Pentru probleme:
1. Verifică `test_system.py`
2. Citește README.md complet
3. Check logs în terminal
4. Verifică requirements.txt

## 🎓 Next Steps

După ce totul funcționează:
1. ✅ Adaugă mai multe imagini pentru accuracy mai bună
2. ✅ Experimentează cu hiperparametri
3. ✅ Adaugă mai multe clase (de ex: cyborg)
4. ✅ Deploy pe cloud (Heroku, AWS, etc.)
5. ✅ Adaugă autentificare în API

---

**Succes la OSACE Hackathon! 🚀**
