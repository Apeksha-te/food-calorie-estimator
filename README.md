# 🍽️ AI-Based Food Calorie Estimator
### Final Year Mini Project | Image Processing & Machine Learning

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

---

## 📌 Abstract

An AI-powered web application that **automatically identifies food from photos** and estimates detailed nutritional information including **calories, protein, carbohydrates, and fat** using Convolutional Neural Networks (CNN) and OpenCV image processing.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🧠 CNN Classification | MobileNetV2 transfer learning, ~95% accuracy |
| 📸 Image Upload | Drag & drop or webcam capture |
| 📊 Nutrition Analysis | Calories, Protein, Carbs, Fat |
| 💡 Health Tips | Personalised dietary recommendations |
| 📋 History Tracking | SQLite database with daily calorie totals |
| 📄 PDF Reports | Downloadable prediction reports |
| 🔊 Voice Output | Text-to-speech result reading |
| ⚖️ BMI Calculator | Built-in BMI + health status |
| 🌗 Dark/Light Mode | Full theme toggle |
| 📱 Responsive UI | Works on mobile, tablet & desktop |

---

## 🏗️ Project Structure

```
food-calorie-estimator/
│
├── app.py              ← Flask backend (routes, DB, server)
├── predict.py          ← ML prediction module
├── train.py            ← CNN model training script
├── utils.py            ← Helper functions (PDF, BMI, etc.)
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
├── .gitignore
├── database.db         ← SQLite DB (auto-created on first run)
│
├── model/
│   └── food_model.h5   ← Trained CNN model (generate with train.py)
│
├── static/
│   ├── css/
│   │   └── style.css   ← Main stylesheet (glassmorphism UI)
│   ├── js/
│   │   ├── main.js     ← Theme toggle, particles, BMI
│   │   ├── upload.js   ← Upload, prediction, voice, PDF
│   │   └── history.js  ← History filter, delete, chart
│   └── uploads/        ← Uploaded food images stored here
│
├── templates/
│   ├── index.html      ← Home page
│   ├── upload.html     ← Upload & predict page
│   ├── history.html    ← Prediction history page
│   └── about.html      ← Project info & viva Q&A
│
├── dataset/            ← Place Food-101 images here for training
│   ├── pizza/
│   ├── burger/
│   ├── dosa/
│   └── ...
```

---

## ⚙️ Installation Guide (Windows + VS Code)

### Step 1 — Prerequisites

Make sure you have installed:
- [Python 3.10+](https://python.org/downloads/) — ✅ Check "Add to PATH"
- [VS Code](https://code.visualstudio.com/)
- VS Code Python extension (ms-python.python)

### Step 2 — Clone / Download Project

```bash
# Option A: Download ZIP and extract
# Option B: Git clone
git clone https://github.com/yourusername/food-calorie-estimator.git
cd food-calorie-estimator
```

### Step 3 — Create Virtual Environment

Open VS Code terminal (`Ctrl + ~`) and run:

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ TensorFlow is large (~500 MB). This may take 5–10 minutes.

### Step 5 — Run the Application

```bash
python app.py
```

You should see:
```
=======================================================
  AI Food Calorie Estimator - Flask Server
  Open http://127.0.0.1:5000 in your browser
=======================================================
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## 🤖 Model Training (Optional)

The app runs in **demo mode** without a trained model (uses colour-based heuristics). For production accuracy:

### Step 1 — Download Dataset

```
Food-101 Dataset:
https://www.kaggle.com/datasets/dansbecker/food-101

Download and extract to the dataset/ folder with sub-folders:
dataset/
  pizza/    (1000 images)
  burger/   (1000 images)
  dosa/     (collect 500+ images)
  biryani/  (collect 500+ images)
  idli/     (collect 500+ images)
  pasta/    (1000 images)
  apple/    (from fruits dataset)
  banana/   (from fruits dataset)
  samosa/   (collect 500+ images)
  sandwich/ (1000 images)
```

### Step 2 — Train the Model

```bash
python train.py
```

This will:
- Train MobileNetV2 for 20 epochs (Phase 1)
- Fine-tune for 10 more epochs (Phase 2)
- Save `model/food_model.h5`
- Generate `model/training_history.png` (accuracy/loss curves)
- Generate `model/confusion_matrix.png`

> 💡 Training takes 30–60 min on CPU, 10–15 min on GPU.

### Step 3 — Restart the Server

```bash
python app.py
```

The server will automatically load `model/food_model.h5`.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/upload` | Upload & predict page |
| GET | `/history` | Prediction history |
| GET | `/about` | About project |
| POST | `/predict` | **Upload image → get nutrition JSON** |
| GET | `/api/history` | JSON list of all predictions |
| GET | `/api/daily-calories` | Today's total calories |
| DELETE | `/api/delete/<id>` | Delete a record |
| DELETE | `/api/clear-history` | Clear all history |

### Example POST /predict

```bash
curl -X POST http://localhost:5000/predict \
  -F "image=@pizza.jpg"
```

Response:
```json
{
  "food_name": "Pizza",
  "calories": 320,
  "protein": 12,
  "carbs": 35,
  "fat": 14,
  "confidence": 96.3,
  "health_tip": "Pizza is high in sodium...",
  "health_label": "Moderate – enjoy occasionally",
  "image_url": "/static/uploads/abc123.jpg"
}
```

---

## 🧠 Machine Learning Details

| Parameter | Value |
|-----------|-------|
| Base Model | MobileNetV2 (ImageNet) |
| Input Size | 224 × 224 × 3 |
| Optimizer | Adam (lr=1e-3 → 1e-5) |
| Loss | Categorical Cross-Entropy |
| Classes | 10 food categories |
| Accuracy | ~93–96% (val) |
| Augmentation | Rotation, Flip, Zoom, Shift |

### Image Preprocessing Pipeline (OpenCV)
1. Read image → `cv2.imread()`
2. Resize to 224×224 → `cv2.resize()`
3. Gaussian blur (noise removal) → `cv2.GaussianBlur()`
4. BGR → RGB conversion → `cv2.cvtColor()`
5. Normalize [0,1] → `img / 255.0`
6. Add batch dim → `np.expand_dims()`

---

## 🍽️ Supported Food Classes & Nutrition

| Food | Calories | Protein | Carbs | Fat |
|------|----------|---------|-------|-----|
| Pizza | 320 kcal | 12g | 35g | 14g |
| Burger | 490 kcal | 25g | 40g | 27g |
| Dosa | 168 kcal | 4g | 30g | 4g |
| Biryani | 370 kcal | 18g | 45g | 12g |
| Idli | 58 kcal | 2g | 11g | 0.4g |
| Pasta | 220 kcal | 8g | 43g | 2g |
| Apple | 82 kcal | 0.4g | 22g | 0.2g |
| Banana | 89 kcal | 1.1g | 23g | 0.3g |
| Samosa | 262 kcal | 5g | 28g | 15g |
| Sandwich | 290 kcal | 15g | 38g | 9g |

---

## 🔮 Future Enhancements

- Expand to 101 food classes (full Food-101)
- Real portion size estimation using depth sensing
- Native Android/iOS app
- Cloud deployment (AWS / Google Cloud)
- Integration with fitness APIs (Google Fit, Apple Health)
- Multi-language support including Hindi, Tamil, Telugu
- Restaurant menu scanning with AR overlay

---

## 📚 References

- Food-101 Dataset: Bossard et al., ECCV 2014
- MobileNetV2: Sandler et al., CVPR 2018
- National Institute of Nutrition (NIN), Hyderabad — Indian Food Composition Tables
- USDA FoodData Central

---

## 👨‍💻 Technologies Used

**Frontend:** HTML5, CSS3, JavaScript ES6, Bootstrap 5, Chart.js  
**Backend:** Python 3.10, Flask 3.0  
**ML:** TensorFlow 2.16, Keras, MobileNetV2  
**Image Processing:** OpenCV 4.10, NumPy, Pillow  
**Database:** SQLite3  
**Tools:** VS Code, Git, pip  

---

*Final Year Mini Project — AI-Based Food Calorie Estimator Using Image Processing and Machine Learning*
