# 🎥 Live Feed Detection - Ghid de Utilizare

## Prezentare Generală

Sistemul de detecție live feed permite recunoașterea în timp real a roboților și oamenilor folosind camera web. Oferă analiză continuă a cadrelor video cu overlay-uri vizuale și statistici în timp real.

## ✨ Funcționalități

### 1. **Detecție în Timp Real**
- Procesare continuă a cadrelor video
- Predicții instant afișate pe video
- Overlay-uri colorate (🤖 Purpuriu pentru roboți, 👤 Albastru pentru oameni)

### 2. **Schimbarea Camerei** 🔄
- Comutare între camera frontală și cea din spate
- Buton "Flip" disponibil în timpul rulării
- Mesaj de confirmare la schimbarea camerei

### 3. **Controale Ajustabile**

#### Interval de Detecție (100-2000ms)
- **100-300ms**: Detecție rapidă, consum mare de CPU
- **500ms** (implicit): Echilibru optim între viteză și performanță
- **1000-2000ms**: Detecție mai lentă, consum redus de CPU

#### Prag de Încredere (0-100%)
- **30-50%**: Mai multe detecții, posibile fals pozitive
- **50%** (implicit): Echilibru recomandat
- **70-80%**: Doar detecții foarte sigure

### 4. **Statistici Live**
- **Cadre Procesate**: Total cadre analizate
- **Răspuns Mediu**: Timp mediu de procesare (ms)
- **Ultima Detecție**: Ultima clasificare efectuată
- **FPS Counter**: Cadre pe secundă procesate efectiv

### 5. **Istoric Detecții**
- Ultimele 10 detecții cu timestamp-uri
- Clasă detectată și nivel de încredere
- Actualizare automată

## 🎮 Cum se Folosește

### Pornire Live Feed

1. **Deschide aplicația** în browser
2. **Derulează** până la secțiunea "Live Feed Detection"
3. **Ajustează setările** (opțional):
   - Interval de detecție
   - Prag de încredere
4. **Click pe "Start"** ▶️
5. **Permite accesul** la cameră când browser-ul cere permisiunea

### Schimbarea Camerei

1. **În timpul rulării**, click pe butonul **"🔄 Flip"**
2. **Camera va comuta** automat între frontală/spate
3. **Apare notificare** de confirmare

### Oprire Live Feed

1. **Click pe "Stop"** ⏹️
2. **Camera se închide** automat
3. **Statisticile rămân** afișate

## ⚙️ Setări Recomandate

### Pentru Performanță Maximă
```
Interval de Detecție: 1000-1500ms
Prag de Încredere: 60%
```

### Pentru Acuratețe Maximă
```
Interval de Detecție: 300-500ms
Prag de Încredere: 70%
```

### Pentru Testare Rapidă
```
Interval de Detecție: 100-200ms
Prag de Încredere: 40%
```

## 🔧 Specificații Tehnice

### Backend
- **Endpoint**: `/api/predict-live`
- **Metodă**: POST
- **Format**: multipart/form-data
- **Optimizări**: Fără salvare în bază de date pentru viteză maximă

### Frontend
- **Video Capture**: HTML5 MediaDevices API
- **Canvas Rendering**: 85% JPEG quality
- **Switching Cameras**: facingMode toggle (user/environment)
- **Update Rate**: Configurabil (100-2000ms)

### Suport Dispozitive
- ✅ **Desktop**: Toate browser-ele moderne cu webcam
- ✅ **Mobile**: Android/iOS cu camere frontale și din spate
- ✅ **Tablet**: iPad, Android tablets

## 📱 Funcționalitate pe Mobile

### Cameră Frontală
- Mod selfie pentru detecție față în față
- Ideal pentru demonstrații live

### Cameră din Spate
- Mod principal pentru scanare mediu înconjurător
- Calitate mai bună a imaginii
- Ideal pentru fotografii de obiecte/persoane

## 🎯 Cazuri de Utilizare

### 1. **Securitate în Timp Real**
Detectare continuă a prezenței roboților vs oameni în zone monitorizate.

### 2. **Prezentări Interactive**
Demonstrații live ale capacităților AI la evenimente/conferințe.

### 3. **Colectare Date**
Capturare rapidă de exemple pentru îmbunătățirea modelului.

### 4. **Aplicații Mobile**
Scanare instantanee cu schimbare între camere.

## 🐛 Troubleshooting

### Camera nu pornește
- Verifică permisiunile browser-ului
- Verifică că nicio altă aplicație nu folosește camera
- Reîmprospătează pagina și încearcă din nou

### FPS scăzut
- Crește intervalul de detecție (500-1000ms)
- Verifică utilizarea CPU/GPU
- Închide alte tab-uri/aplicații

### Schimbarea camerei nu funcționează
- Nu toate dispozitivele au ambele camere
- Pe desktop, poate fi disponibilă doar camera frontală
- Verifică setările sistemului de operare

### Detecții inconsistente
- Ajustează pragul de încredere
- Asigură-te că există lumină suficientă
- Menține camera stabilă pentru cadre clare

## 🚀 Performanță

### Metrici Tipice
- **Răspuns**: 200-500ms per cadru
- **FPS**: 1-5 FPS (depinde de interval)
- **Latență**: < 1 secundă de la captură la rezultat

### Optimizări Implementate
- ✅ Compresie JPEG 85%
- ✅ Fără salvare în bază de date
- ✅ Procesare asincronă
- ✅ Canvas rendering optimizat
- ✅ Interval configurabil

## 💡 Tips & Tricks

1. **Lumină Bună**: Asigură-te că scena e bine iluminată
2. **Camera Stabilă**: Evită mișcările bruste
3. **Distanță Optimă**: 50cm - 2m de la subiect
4. **Fundal Simplu**: Reduce zgomotul vizual
5. **Test Ambele Camere**: Compară rezultatele între camere

## 🔐 Confidențialitate

- ❌ **NU se salvează** cadrele video
- ❌ **NU se înregistrează** sesiuni
- ✅ **Procesare locală** pe server-ul tău
- ✅ **Control complet** asupra datelor

## 📊 Diferențe față de Predicție Statică

| Caracteristică | Live Feed | Predicție Statică |
|----------------|-----------|-------------------|
| Viteză | Real-time (1-5 FPS) | Single shot |
| Salvare DB | ❌ Nu | ✅ Da |
| Istoric | Temporar (10 items) | Permanent |
| Cameră | Switching support | Single capture |
| CPU Usage | Continuu | Punctual |
| Use Case | Monitoring | Clasificare |

## 🎓 Exemple de Utilizare

### Monitoring de Securitate
```javascript
// Setări recomandate
Interval: 1000ms
Prag: 70%
Cameră: Spate (environment)
```

### Demo Interactiv
```javascript
// Setări recomandate
Interval: 500ms
Prag: 50%
Cameră: Față (user) - cu switching
```

### Testare Model
```javascript
// Setări recomandate
Interval: 200ms
Prag: 30%
Cameră: Ambele - test comparativ
```

## 📞 Suport

Pentru probleme sau întrebări:
1. Verifică acest ghid
2. Consultă `TROUBLESHOOTING.md`
3. Verifică consola browser-ului pentru erori
4. Testează pe un alt dispozitiv/browser

---

**Versiune**: 1.0.0  
**Data**: 8 Noiembrie 2025  
**Feature**: Live Feed Detection cu Camera Switching
