#!/usr/bin/env python3
"""
generate_synthetic_images.py - Generate synthetic/placeholder images for training
Creates simple colored images for food classes that have no training data yet.
This allows training to proceed while you collect real images.
"""

from PIL import Image, ImageDraw
import random
import os
from pathlib import Path

def generate_synthetic_image(food_class: str, size: tuple = (224, 224), num_images: int = 8) -> None:
    """Generate synthetic images for a food class."""
    dataset_path = Path("dataset") / food_class
    dataset_path.mkdir(parents=True, exist_ok=True)
    
    # Color schemes for different foods
    color_schemes = {
        "pizza": [(255, 165, 0), (220, 20, 60), (255, 215, 0)],      # Orange, Crimson, Gold
        "burger": [(139, 69, 19), (160, 82, 45), (210, 105, 30)],    # Brown shades
        "dosa": [(210, 180, 140), (188, 143, 143), (205, 133, 63)],  # Tan shades
        "biryani": [(139, 35, 69), (185, 85, 59), (205, 92, 92)],    # Deep brown/red
        "idli": [(240, 240, 240), (220, 220, 220), (200, 200, 200)], # White/gray
        "pasta": [(255, 215, 0), (210, 180, 140), (218, 165, 32)],   # Yellow/gold
        "apple": [(220, 20, 60), (255, 0, 0), (139, 0, 0)],          # Red shades
        "banana": [(255, 215, 0), (255, 255, 0), (218, 165, 32)],    # Yellow shades
        "samosa": [(188, 143, 143), (160, 82, 45), (205, 133, 63)],  # Brown shades
        "sandwich": [(210, 180, 140), (160, 82, 45), (139, 69, 19)], # Tan/brown
        "rice": [(255, 255, 255), (245, 245, 245), (240, 240, 240)], # White shades
    }
    
    colors = color_schemes.get(food_class, [(200, 200, 200)])
    
    for i in range(num_images):
        # Create image with random background color
        bg_color = random.choice(colors)
        img = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add some texture/pattern
        for _ in range(50):
            x = random.randint(0, size[0])
            y = random.randint(0, size[1])
            radius = random.randint(5, 30)
            shade_variation = random.randint(-30, 30)
            color_adjusted = tuple(max(0, min(255, c + shade_variation)) for c in bg_color)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color_adjusted)
        
        # Save image
        img_path = dataset_path / f"synthetic_{food_class}_{i:02d}.png"
        img.save(img_path)
        print(f"  ✓ Created: {img_path.name}")

if __name__ == "__main__":
    print("🎨 Generating synthetic images for empty folders...\n")
    
    empty_classes = ["idli", "pasta", "samosa", "sandwich"]
    
    for food_class in empty_classes:
        print(f"Generating images for {food_class}...")
        generate_synthetic_image(food_class, num_images=8)
    
    print("\n✓ Synthetic images created!")
    print("\nDataset Summary:")
    print("-" * 60)
    
    for food_class in ["pizza", "burger", "dosa", "biryani", "idli", "pasta", "apple", "banana", "samosa", "sandwich", "rice"]:
        class_path = Path("dataset") / food_class
        count = len(list(class_path.glob("*")))
        print(f"{food_class:<15}: {count:>3} images")
    
    print("-" * 60)
    print("\n✓ Ready for training! Run: python train.py")
