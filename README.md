Documentație Proiect: Clasificare Oameni vs Roboți


1.Introducere:

Acest proiect are ca obiectiv dezvoltarea unui sistem automat de recunoaștere vizuală capabil să distingă între imagini care conțin oameni și imagini care conțin roboți. Sistemul se bazează pe un model de tip CNN (Convolutional Neural Network) antrenat folosind metoda Transfer Learning cu arhitectura MobileNetV2. Aplicația include o interfață web pentru încărcarea imaginilor și vizualizarea rezultatului în timp real, precum și un backend care salvează predicțiile într-o bază de date Supabase.


2. Structura Proiectului

osace-hackathon/
├── backend/
│   ├── app.py              # Server Flask (API + UI)
│   ├── config.py           # Configurații aplicație și model
│   ├── supabase_db.py      # Operare cu baza de date Supabase
│   └── uploads/            # Fișiere temporare uploadate
├── model/
│   ├── cnn_model.py        # Definire arhitectură CNN
│   ├── train.py            # Script pentru antrenarea modelului
│   ├── prepare_dataset.py  # Script pregătire dataset
│   └── robot_vs_human_classifier.h5  # Modelul antrenat
├── data/
│   ├── raw/                # Date brute (human/, robot/)
│   ├── train/              # Date pentru antrenament
│   ├── val/                # Date pentru validare
│   └── test/               # Date pentru testare
└── frontend/
    └── index.html          # Interfață web






3. Fluxul Sistemului

1.	Utilizatorul încarcă o imagine prin interfață.
2.	Backend-ul Flask primește și preprocesează imaginea (resize 224x224, normalizare).
3.	Modelul CNN returnează predicția (human sau robot) și probabilitatea (confidence).
4.	Predicția este salvată în Supabase.
5.	Rezultatul este afișat pe interfața web.



4. Arhitectura Modelului CNN

Modelul folosește MobileNetV2 pre-antrenat pe ImageNet, cu stratul final înlocuit pentru clasificare binară.

Caracteristici:

•	Input: 224x224x3
•	Straturi MobileNetV2 înghețate
•	GlobalAveragePooling2D
•	Dense (128) + ReLU
•	Dropout (0.3)
•	Dense (2) + Softmax

Parametri antrenare:

Epoci: 10 
Batch size: 32 
Optimizer: Adam
Loss: Categorial Crossentropy
Metrici: Accuracy, Precision, Recall

5. API Flask

Endpoint	Metodă	Descriere
/api/predict	POST	Primește o imagine și returnează predicția
/api/history	GET	Returnează ultimele predicții
/api/statistics	GET	Returnează statistici agregate
/health	GET	Verifică dacă serverul funcționează


6.Interfața Web

Interfața din index.html permite:

•	Încărcare imagini (drag & drop)
•	Afișarea rezultatului predicției
•	Vizualizarea istoricului și statisticilor



7. Baza de Date Supabase

Tabel utilizat: classification 
Coloană	Tip	Descriere
id	integer	Cheie primară
filename	text	Numele fișierului
predicted_class	text	human / robot / unknown
confidence	float	Încredere model
User_feedback	text	Feedback-ul userului
Created_at	timestamp	Moment salvare
		
		
		
		
		
		
		
8. Funcționalități ale Aplicației Web

Aplicația include o interfață web intuitivă și complet integrată cu API-ul backend și baza de date.

8.1 Încărcare Imagini (Upload)
•	Utilizatorul poate încărca imagini prin buton sau drag & drop.
•	Imaginile sunt trimise către API pentru clasificare.
•	Rezultatul este afișat vizual, alături de scorul de încredere.

8.2 Clasificare în Timp Real (Live Camera Feed)
•	Sistemul permite capturarea de imagini direct din camera web.
•	Fiecare frame este trimis către server pentru analiză.
•	Predicțiile sunt afișate live și se salvează în baza de date.


8.3 Istoric Predicții
•	Aplicația afișează lista ultimelor clasări efectuate.
•	Fiecare intrare conține:
o	Numele imaginii
o	Clasa prezisă (Human / Robot)
o	Probabilitatea asociată
o	Data și ora

8.4 Statistici și Vizualizare Date
•	Afișare număr total de predicții.
•	Raport între imagini identificate ca Human vs Robot.
•	Media scorurilor de încredere.

8.5 Persistență în Supabase
•	Toate predicțiile sunt salvate automat.
•	Datele pot fi exportate pentru analiză ulterioară.


9. Concluzii

Acest proiect prezintă un flux complet de Machine Learning, incluzând:
•	Pregătirea și organizarea datasetului
•	Antrenarea modelului prin transfer learning
•	Dezvoltarea unui API funcțional cu Flask
•	Realizarea unei interfețe web interactive
•	Persistență și analiză date prin Supabase
Proiectul poate fi extins pentru:
•	Suport pentru stream video în timp real
•	Clasificare multi-clasă
•	Integrare cu sisteme IoT

