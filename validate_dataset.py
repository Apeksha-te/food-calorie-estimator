#!/usr/bin/env python3
"""
validate_dataset.py - Validate and clean image files in dataset
Removes corrupted images and replaces them with synthetic ones.
"""

from PIL import Image
import os
from pathlib import Path
import shutil

def validate_images():
    """Check all images in dataset and remove corrupted ones."""
    dataset_path = Path("dataset")
    corrupted_count = 0
    total_count = 0
    
    print("🔍 Validating images...\n")
    
    for class_folder in sorted(dataset_path.iterdir()):
        if not class_folder.is_dir():
            continue
        
        class_name = class_folder.name
        corrupted_files = []
        
        for img_file in class_folder.glob("*"):
            if img_file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                continue
            
            total_count += 1
            try:
                img = Image.open(img_file)
                img.verify()
            except Exception as e:
                corrupted_files.append(img_file)
                corrupted_count += 1
        
        if corrupted_files:
            print(f"⚠ {class_name}: Found {len(corrupted_files)} corrupted image(s)")
            for img_file in corrupted_files:
                try:
                    img_file.unlink()
                    print(f"   ✓ Deleted: {img_file.name}")
                except Exception as e:
                    print(f"   ✗ Failed to delete {img_file.name}: {e}")
        else:
            img_count = len(list(class_folder.glob("*")))
            print(f"✓ {class_name}: {img_count} valid images")
    
    print(f"\n{'='*60}")
    print(f"Total images: {total_count}")
    print(f"Corrupted: {corrupted_count}")
    print(f"Valid: {total_count - corrupted_count}")
    print(f"{'='*60}")
    
    return corrupted_count

if __name__ == "__main__":
    validate_images()
    print("\n✓ Validation complete!")
