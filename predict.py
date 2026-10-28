# ============================================================
# predict.py - Food prediction using the trained CNN model
# Works together with train.py (same label order, same preprocessing)
# ============================================================

import os
import json
import cv2
import numpy as np

NUTRITION_DB = {
    "pizza": {"calories": 320, "protein": 12, "carbs": 35, "fat": 14,
        "tip": "Pizza is high in sodium and saturated fat. Opt for thin crust, load with veggies, and limit to 1-2 slices.",
        "health_label": "Moderate – enjoy occasionally"},
    "burger": {"calories": 490, "protein": 25, "carbs": 40, "fat": 27,
        "tip": "Burgers are calorie-dense. Choose grilled over fried, skip extra sauce, and pair with a salad instead of fries.",
        "health_label": "High Calorie – limit intake"},
    "rice": {"calories": 206, "protein": 4.3, "carbs": 45, "fat": 0.4,
        "tip": "Plain rice is a good source of carbohydrates. Pair with vegetables and lean protein for a balanced meal.",
        "health_label": "Moderate – balance with proteins and veggies"},
    "dosa": {"calories": 168, "protein": 4, "carbs": 30, "fat": 4,
        "tip": "Dosa is a healthy fermented food. Rich in probiotics, low fat. Pair with sambar and chutney for a balanced meal.",
        "health_label": "Healthy – great choice!"},
    "biryani": {"calories": 370, "protein": 18, "carbs": 45, "fat": 12,
        "tip": "Biryani provides good protein from meat/eggs. Control portion size and pair with raita for digestion.",
        "health_label": "Moderate – watch portions"},
    "idli": {"calories": 58, "protein": 2, "carbs": 11, "fat": 0.4,
        "tip": "Idli is one of the healthiest Indian foods – steamed, low calorie, easy to digest. Excellent breakfast choice!",
        "health_label": "Very Healthy – highly recommended"},
    "pasta": {"calories": 220, "protein": 8, "carbs": 43, "fat": 2,
        "tip": "Choose whole wheat pasta for more fibre. Go light on cream sauces; tomato-based sauces are healthier.",
        "health_label": "Moderate – choose wisely"},
    "apple": {"calories": 82, "protein": 0.4, "carbs": 22, "fat": 0.2,
        "tip": "An apple a day keeps the doctor away! Rich in fibre and antioxidants. Great snack for weight management.",
        "health_label": "Very Healthy – excellent choice!"},
    "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3,
        "tip": "Bananas are high in potassium and natural energy. Perfect pre-workout snack. Limit if managing blood sugar.",
        "health_label": "Healthy – great natural energy"},
    "samosa": {"calories": 262, "protein": 5, "carbs": 28, "fat": 15,
        "tip": "Samosas are deep-fried and calorie-rich. Baked samosas are a healthier option. Enjoy in moderation.",
        "health_label": "High Fat – enjoy occasionally"},
    "sandwich": {"calories": 290, "protein": 15, "carbs": 38, "fat": 9,
        "tip": "Choose whole grain bread, lean protein, and load with vegetables. Avoid mayo-heavy spreads.",
        "health_label": "Moderate – healthy if well-made"},
}

IMG_SIZE = 224
CONFIDENCE_THRESHOLD = 50.0     # below this % the app says "Not Sure"
MODEL_PATH = os.path.join("model", "food_model.h5")
LABELS_PATH = os.path.join("model", "labels.json")

_MODEL = None
_LABELS = None


def preprocess_image(image_path: str) -> np.ndarray:
    """Read, resize, BGR->RGB. NO /255 and NO blur: scaling is inside the model."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
    return np.expand_dims(img, axis=0)


def load_model():
    global _MODEL, _LABELS
    if not os.path.exists(MODEL_PATH) or not os.path.exists(LABELS_PATH):
        raise RuntimeError(
            "Trained model not found. Run train.py first to create "
            "model/food_model.h5 and model/labels.json")
    from tensorflow.keras.models import load_model as keras_load
    _MODEL = keras_load(MODEL_PATH)
    with open(LABELS_PATH) as f:
        _LABELS = json.load(f)
    print("[predict.py] Trained model loaded successfully.")


def predict_food(image_path: str) -> dict:
    if _MODEL is None:
        load_model()

    probs = _MODEL.predict(preprocess_image(image_path), verbose=0)[0]
    idx = int(np.argmax(probs))
    confidence = round(float(probs[idx]) * 100, 1)
    food_name = _LABELS[idx]

    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "food_name": "Not Sure", "calories": 0, "protein": 0, "carbs": 0,
            "fat": 0, "confidence": confidence,
            "health_tip": "The model is not confident about this image. Try a clearer, closer photo with good lighting.",
            "health_label": "Unknown",
        }

    n = NUTRITION_DB[food_name]
    return {
        "food_name": food_name.title(),
        "calories": n["calories"], "protein": n["protein"],
        "carbs": n["carbs"], "fat": n["fat"],
        "confidence": confidence,
        "health_tip": n["tip"], "health_label": n["health_label"],
    }