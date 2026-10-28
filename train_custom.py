#!/usr/bin/env python3
"""
train_custom.py - Train a lightweight custom CNN from scratch
No pre-trained weights, minimal memory usage, good for Windows systems.
"""

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("Training Lightweight Custom CNN Model")
print("=" * 70)

IMG_SIZE = 128  # Smaller size for lower memory
BATCH_SIZE = 4
EPOCHS = 20
CLASS_NAMES = ["pizza", "burger", "dosa", "biryani", "idli", "pasta", 
               "apple", "banana", "samosa", "sandwich", "rice"]

print("\n[Step 1] Loading dataset...")
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

print(f"✓ Loaded {generator.samples} images")

print("\n[Step 2] Building lightweight CNN model...")
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D((2, 2)),
    
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(len(CLASS_NAMES), activation='softmax')
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"Model parameters: {model.count_params():,}")
print(model.summary())

print("\n[Step 3] Training...")
model.fit(
    generator,
    epochs=EPOCHS,
    callbacks=[
        ModelCheckpoint('model/food_model.h5', monitor='accuracy', save_best_only=True, verbose=0)
    ],
    verbose=1
)

print("\n" + "=" * 70)
print("✓ Training Complete!")
print("=" * 70)
print("Model saved to: model/food_model.h5")
