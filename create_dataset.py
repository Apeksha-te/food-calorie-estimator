#!/usr/bin/env python3
"""
create_dataset.py - Automatically download food images for training
Description: Downloads ~12-15 sample images per food class using Bing Image Search
             and organizes them into dataset/ folders for training.
"""

import os
import sys
import time
from pathlib import Path

def download_images_bing():
    """Download images using bing-image-downloader"""
    try:
        from bing_image_downloader import downloader
    except ImportError:
        print("[ERROR] bing-image-downloader not found. Installing...")
        os.system(f"{sys.executable} -m pip install bing-image-downloader")
        from bing_image_downloader import downloader

    # Food classes and search queries
    food_classes = {
        "pizza": "pizza food dish",
        "burger": "hamburger burger fast food",
        "dosa": "dosa Indian food",
        "biryani": "biryani Indian rice dish",
        "idli": "idli South Indian food",
        "pasta": "pasta Italian food",
        "apple": "red apple fruit",
        "banana": "banana yellow fruit",
        "samosa": "samosa Indian snack",
        "sandwich": "sandwich bread",
        "rice": "cooked rice food"
    }

    dataset_path = Path("dataset")
    total_downloaded = 0

    for food_class, query in food_classes.items():
        class_folder = dataset_path / food_class
        
        # Skip if folder already has enough images (>10)
        existing_images = len(list(class_folder.glob("*.jpg"))) + len(list(class_folder.glob("*.png")))
        if existing_images > 10:
            print(f"✓ {food_class}: Already has {existing_images} images. Skipping...")
            continue

        print(f"\n📥 Downloading images for '{food_class}' ({query})...")
        try:
            downloader.download(
                query,
                limit=15,
                output_dir="dataset_temp",
                adult_filter_off=True,
                force_replace=False,
                timeout=20,
                verbose=False
            )

            # Move downloaded images to the correct folder
            temp_folder = Path("dataset_temp") / query
            if temp_folder.exists():
                downloaded_count = 0
                for img_file in temp_folder.glob("*"):
                    if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                        dest = class_folder / f"{food_class}_{int(time.time() * 1000) % 100000}_{img_file.name}"
                        try:
                            img_file.rename(dest)
                            downloaded_count += 1
                        except Exception as e:
                            print(f"   ⚠ Failed to move {img_file.name}: {e}")
                
                print(f"   ✓ Saved {downloaded_count} images to {class_folder}")
                total_downloaded += downloaded_count

                # Clean up temp folder
                try:
                    temp_folder.rmdir()
                except:
                    pass

        except Exception as e:
            print(f"   ⚠ Error downloading {food_class}: {e}")

        time.sleep(1)  # Be respectful to the server

    # Clean up temp directory
    try:
        import shutil
        if Path("dataset_temp").exists():
            shutil.rmtree("dataset_temp")
    except:
        pass

    print(f"\n{'='*60}")
    print(f"✓ Download complete! Total images downloaded: {total_downloaded}")
    print(f"{'='*60}\n")

    # Verify dataset
    print("Dataset Summary:")
    print("-" * 60)
    for food_class in food_classes.keys():
        class_folder = dataset_path / food_class
        count = len(list(class_folder.glob("*")))
        status = "✓" if count > 5 else "⚠"
        print(f"{status} {food_class:<15}: {count:>3} images")
    print("-" * 60)

    return total_downloaded > 50  # True if we have a reasonable dataset

if __name__ == "__main__":
    print("🍕 Food Dataset Creator")
    print("=" * 60)
    print("Downloading food images for training...\n")
    
    success = download_images_bing()
    
    if success:
        print("\n✓ Dataset ready! You can now run: python train.py")
    else:
        print("\n⚠ Dataset has limited images. Consider adding more manually.")
        print("   Run: python train.py anyway (may need more images for optimal accuracy)")
