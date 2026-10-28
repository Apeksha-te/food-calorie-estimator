#!/usr/bin/env python3
"""
test_model.py - Test the trained model with sample images
"""

from predict import predict_food
from pathlib import Path

# Test with first few images from each class
test_classes = {
    "pizza": "dataset/pizza",
    "biryani": "dataset/biryani",
    "dosa": "dataset/dosa",
    "burger": "dataset/burger",
    "apple": "dataset/apple"
}

print("🧪 Testing Trained Model")
print("=" * 70)

for food_class, folder_path in test_classes.items():
    folder = Path(folder_path)
    images = list(folder.glob("*.*"))[:2]  # Get first 2 images
    
    if not images:
        print(f"\n⚠ No images found in {food_class} folder")
        continue
    
    print(f"\n📂 Testing {food_class.upper()} (from {food_class} folder):")
    print("-" * 70)
    
    for img_path in images:
        try:
            result = predict_food(str(img_path))
            predicted = result["food_name"]
            confidence = result["confidence"]
            correct = "✓" if predicted.lower() == food_class.lower() else "✗"
            
            print(f"{correct} {img_path.name:<40} → {predicted} ({confidence}%)")
        except Exception as e:
            print(f"✗ {img_path.name:<40} → ERROR: {e}")

print("\n" + "=" * 70)
print("✓ Model test complete!")
