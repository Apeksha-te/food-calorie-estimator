#!/usr/bin/env python3
"""
train_lightweight.py - Lightweight transfer learning for Windows
Uses MobileNetV2 with minimal memory footprint.
"""

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from pathlib import Path
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("Training Food Classification Model - Transfer Learning")
print("=" * 70)

IMG_SIZE = 224
BATCH_SIZE = 4  # Reduced to avoid memory issues
EPOCHS = 20
CLASS_NAMES = ["pizza", "burger", "dosa", "biryani", "idli", "pasta", 
               "apple", "banana", "samosa", "sandwich", "rice"]

print("\n[Step 1] Preparing dataset...")
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True
)

generator = datagen.flow_from_directory(
    "dataset",
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

print(f"Total images: {generator.samples}")

print("\n[Step 2] Building model...")
# Load pre-trained base
base_model = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights='imagenet')
base_model.trainable = False

# Simple model
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(len(CLASS_NAMES), activation='softmax')
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"Parameters: {model.count_params():,}")

print("\n[Step 3] Training...")
model.fit(
    generator,
    epochs=EPOCHS,
    callbacks=[ModelCheckpoint('model/food_model.h5', save_best_only=True, verbose=0)],
    verbose=1
)

print("\n[Step 4] Fine-tuning...")
base_model.trainable = True
for layer in base_model.layers[:-10]:
    layer.trainable = False

model.compile(
    optimizer=Adam(learning_rate=0.00001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    generator,
    epochs=3,
    callbacks=[ModelCheckpoint('model/food_model.h5', save_best_only=True, verbose=0)],
    verbose=1
)

print("\n✓ Model saved to model/food_model.h5")
