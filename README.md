# Robot vs Human CNN Classifier

Prototip funcțional de clasificare a imaginilor folosind CNN (Convolutional Neural Network) pentru detectarea roboților vs oameni.

## Quick Start

Doar două comenzi pentru a porni totul:

```powershell
# Terminal 1: Start Flask (API + Frontend)
python backend/app.py

# Terminal 2: Start ngrok pentru acces remote
ngrok http 5000
```

Apoi deschide URL-ul ngrok în browser.

---

## Descriere

Acest proiect implementează un sistem complet de clasificare a imaginilor care include:
- Model CNN antrenat cu TensorFlow/Keras
- Transfer learning cu EfficientNet (B0–B3, configurabil) și fine‑tuning pe straturile finale
- API REST cu Flask pentru predicții
- Interfață web modernă pentru testare
- Integrare cu Supabase pentru persistența datelor
- Augmentare automată a datelor
- Raportare completă a metricilor (accuracy, loss, precision, recall)

## Model și rezultate

- Backbone EfficientNet-B0 preantrenat pe ImageNet, cu head personalizat (GlobalAveragePooling + Dense 256 + Dropout + Dense softmax).
- Antrenare executată 15 epoci (straturi EfficientNet înghețate) cu batch 32 și learning-rate 5e-4.
- Performanțe obținute înainte de etapa de fine-tuning:
  - **Accuracy set antrenare**: 98.97%
  - **Accuracy set validare**: 100%
  - **Accuracy set test**: 99.56% (loss 0.0157, precision = recall = 99.56%)
- A doua fază (fine-tuning pe ultimele 50 straturi la lr=1e-5) a fost întreruptă din cauza unui fișier JPEG corupt; dataset-ul a fost curățat, iar finalizarea fine-tuning-ului rămâne ca next step.
- Evoluția metricei de-a lungul epocilor (extrasă din `training_report.json`):

Datasetul utilizat pentru această rulare este [Robot Finder – Roboflow Universe](https://universe.roboflow.com/robot-detecktor/robot-finder-anfwl), aproximativ ~3.1k imagini împărțite 70/15/15. + aprox. 100 poze adăugate din drive-ul Osace Hackathon.


## Cerințe îndeplinite

- **Dataset**: Robot vs Human (imagini publice) – preluat de la [roboflow.com](https://universe.roboflow.com/robot-detecktor/robot-finder-anfwl)  
- **Model CNN**: Transfer learning cu EfficientNet + head custom și fine-tuning configurabil  
- **Preprocesare**: Redimensionare (224x224 implicit), normalizare EfficientNet, augmentare extinsă  
- **Split date**: 70% train, 15% validation, 15% test  
- **Antrenare**: 15 epoci + fine-tuning suplimentar (opțional) cu raportare metrici  
- **Export model**: Format .h5 pentru refolosire  
- **API Flask**: Endpoints pentru predicții, statistici și raportare “unknown” când scorul e sub prag  
- **Persistență**: Salvare automată în Supabase (filename, predicted_class, confidence, timestamp)  
- **Interfață web**: Upload imagini + afișare rezultate în timp real  

## Structura Proiectului

```
osace-hackathon/
├── backend/
│   ├── app.py              # Flask API server
│   ├── config.py           # Configurări (Supabase, model, etc.)
│   ├── supabase_db.py      # Client Supabase pentru DB
│   ├── requirements.txt    # Dependențe Python
│   └── uploads/            # Imagini încărcate
├── model/
│   ├── cnn_model.py        # Arhitectura CNN
│   ├── train.py            # Script antrenare
│   ├── prepare_dataset.py  # Pregătire și split dataset
│   └── robot_vs_human_classifier.h5  # Model antrenat
├── data/
│   ├── raw/                # Date brute (human/, robot/)
│   ├── train/              # Date antrenare
│   ├── val/                # Date validare
│   └── test/               # Date testare
├── frontend/
│   └── index.html          # Interfață web
└── README.md
```

## Setup și Instalare

### 1. Prerequisite

- Python 3.8+ instalat
- pip (Python package manager)
- Minim 2GB RAM disponibil
- Conexiune internet pentru descărcare dependențe

### 2. Instalare Dependențe

```powershell
# Navigați la directorul backend
cd backend

# Instalați dependențele
pip install -r requirements.txt
```

### 3. Pregătire Dataset

```powershell
# Navigați la directorul model
cd ../model

# Rulați scriptul de pregătire
python prepare_dataset.py
```

**Important**: După rularea scriptului, adăugați imaginile în:
- `data/raw/human/` - imagini cu oameni
- `data/raw/robot/` - imagini cu roboți

Dataset-ul folosit în experimentul curent provine din:  
[https://universe.roboflow.com/robot-detecktor/robot-finder-anfwl](https://universe.roboflow.com/robot-detecktor/robot-finder-anfwl)
La acest dataset au fost adaugate și aproximativ 200 poze(human+robot) din drive-ul Osace Hackathon

După adăugarea imaginilor, rulați din nou:
```powershell
python prepare_dataset.py
```

### 4. Antrenare Model

```powershell
# Antrenează modelul (15 epoci + fine-tuning)
python train.py
```

Acest script va:
- Încărca datele din `data/train` și `data/val`
- Antrena modelul CNN
- Salva modelul în `model/robot_vs_human_classifier.h5`
- Regenera graficele și rapoartele (`assets/training_history.png`, `training_report.json`)
- Crea raport JSON (`training_report.json`)

**Timp estimat**: 5-30 minute (depinde de dataset și hardware)

### 5. Pornire Server API

```powershell
# Navigați la backend
cd ../backend

# Porniți serverul Flask
python app.py
```

Serverul va porni pe `http://localhost:5000`

### 6. Accesare Interfață Web

Deschideți browser-ul la: **http://localhost:5000**

## Utilizare

### Interfața Web

1. **Upload imagine**: Click pe zona de upload sau drag & drop
2. **Analizare**: Click pe butonul "Analizează Imaginea"
3. **Rezultate**: Vezi clasa prezisă (Human/Robot) și încrederea (confidence)
4. **Statistici**: Monitorizează numărul total de predicții
5. **Istoric**: Vezi ultimele 10 predicții

### API Endpoints

#### POST `/api/predict`
Predicție pentru o imagine

**Request**: multipart/form-data cu field `image`

**Response**:
```json
{
  "success": true,
  "filename": "20231108_143022_image.jpg",
  "predicted_class": "robot",
  "confidence": 0.95,
  "all_probabilities": {
    "human": 0.05,
    "robot": 0.95
  },
  "decision_details": {
    "best_class": "robot",
    "best_confidence": 0.95,
    "second_class": "human",
    "second_confidence": 0.05,
    "margin": 0.90,
    "is_confident": true
  },
  "timestamp": "2023-11-08T14:30:22"
}
```

#### GET `/api/history?limit=10`
Istoric predicții din Supabase

**Response**:
```json
{
  "success": true,
  "count": 10,
  "predictions": [...]
}
```

#### GET `/api/statistics`
Statistici generale

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total": 156,
    "humans": 82,
    "robots": 74,
    "avg_confidence": 0.87
  }
}
```

#### GET `/api/model-info`
Informații despre model

#### GET `/health`
Health check pentru server

## Configurare

Toate configurările se află în `backend/config.py`:

- **SUPABASE_URL**: URL-ul bazei de date Supabase
- **SUPABASE_KEY**: API key pentru Supabase
- **MODEL_BACKBONE**: EfficientNet utilizat (`efficientnet_b0` implicit, suport B1–B3)
- **MODEL_INPUT_SIZE**: Dimensiune input imagini (se ajustează automat pentru backbone)
- **EPOCHS**: Număr epoci antrenare (15)
- **BATCH_SIZE**: Dimensiune batch (32)
- **LEARNING_RATE**: Learning rate inițial (0.0005)
- **FINE_TUNE_AT / FINE_TUNE_EPOCHS**: Control pentru deblocarea ultimelor straturi EfficientNet
- **PREDICTION_THRESHOLD / PREDICTION_MARGIN**: Praguri pentru a raporta `unknown`

## Metrici și Performance

### Rezumat rulare curentă (15 epoci, EfficientNet-B0)

- **Accuracy train**: 0.9897  
- **Accuracy val**: 1.0000  
- **Accuracy test**: 0.9956  
- **Loss test**: 0.0157  
- **Precision/Recall test**: 0.9956  
- **Learning rate schedule**: ReduceLROnPlateau (a scăzut la 2.5e-4 pe final)

- `assets/training_history.png` – evoluția accuracy/loss/precision/recall (train vs val)

## Baza de Date (Supabase)

### Tabel: `predictions`

| Coloană | Tip | Descriere |
|---------|-----|-----------|
| id | integer | Primary key (auto) |
| filename | text | Numele fișierului |
| predicted_class | text | human sau robot |
| confidence | float | Încredere (0-1) |
| timestamp | timestamp | Data și ora predicției |

### Creare tabel (SQL)

```sql
CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  predicted_class TEXT NOT NULL,
  confidence FLOAT NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## Testare

### Test conexiune Supabase
```powershell
cd backend
python supabase_db.py
```

### Test creare model
```powershell
cd model
python cnn_model.py
```

### Test API
```powershell
curl http://localhost:5000/health
```

## Caracteristici Tehnice

### Model CNN
- **Arhitectură**: Transfer learning cu EfficientNet (B0 implicit)
- **Input**: 224x224x3 (RGB) pentru B0 (se ajustează pentru B1/B2/B3)
- **Output**: 2 clase (softmax)
- **Layers custom**: Dense layers + Dropout pentru regularization
- **Optimizer**: Adam cu learning rate 5e-4 (fine-tuning la 1e-5)
- **Loss**: Categorical crossentropy
- **Fine-tuning**: Ultimele 50 de straturi EfficientNet deblocate în etapa a doua

### Augmentare Date
- Random flip (horizontal)
- Random rotation (±30%)
- Random zoom (±25%)
- Random contrast (±30%)
- Random brightness (±20%)

### Preprocesare
- Resize la dimensiunea cerută de EfficientNet
- Normalizare folosind `keras.applications.efficientnet.preprocess_input`
- Conversie RGB

## Troubleshooting

### Model nu se încarcă
- Verificați că `model/robot_vs_human_classifier.h5` există
- Rulați `python model/train.py` pentru a antrena modelul

### Eroare Supabase
- Verificați conexiunea internet
- Confirmați API key și URL în `backend/config.py`
- Verificați că tabelul `predictions` există în Supabase

### Imagini nu apar
- Verificați că directorul `data/raw/human` și `data/raw/robot` conțin imagini
- Rulați din nou `python model/prepare_dataset.py`

### Acuratețe scăzută
- Adăugați mai multe imagini (200+ per clasă)
- Creșteți numărul de epoci în `config.py`
- Verificați calitatea imaginilor din dataset

## Tehnologii Utilizate

- **Deep Learning**: TensorFlow 2.15, Keras
- **Backend**: Flask 3.0, Flask-CORS
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Image Processing**: Pillow, OpenCV
- **Visualization**: Matplotlib
- **Utils**: NumPy, scikit-learn

## Echipa

Proiect dezvoltat pentru OSACE Hackathon

## Licență

Acest proiect este creat în scop educațional pentru OSACE Hackathon.

## Referințe

- TensorFlow Documentation: https://www.tensorflow.org/
- Keras Applications: https://keras.io/api/applications/
- MobileNetV2: https://arxiv.org/abs/1801.04381
- Flask Documentation: https://flask.palletsprojects.com/
- Supabase Docs: https://supabase.com/docs

---
## Acces rapid la aplicație

Scanează QR-ul pentru a deschide interfața web:
Atenție! Pentru ca aplicația să funcționeze trebuie ca serverul să fie pornit. În această clipă serverul este laptop-ul lui Alex.

![QR code pentru aplicație](assets/QrCode.jpg)
