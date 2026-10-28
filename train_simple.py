#!/usr/bin/env python3
"""
train_simple.py - Simple transfer learning with pre-trained MobileNetV2
Uses the current dataset to fine-tune for our 11 food classes.
"""

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import warnings
warnings.filterwarnings('ignore')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TF warnings

print("=" * 70)
print("Training Food Classification Model with Transfer Learning")
print("=" * 70)

IMG_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 25
CLASS_NAMES = ["pizza", "burger", "dosa", "biryani", "idli", "pasta", 
               "apple", "banana", "samosa", "sandwich", "rice"]

dataset_path = Path("dataset")

print("\n[Step 1] Preparing dataset...")
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest'
)

data_generator = datagen.flow_from_directory(
    str(dataset_path),
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

print(f"Total samples: {data_generator.samples}")
print(f"Classes: {list(data_generator.class_indices.keys())}")

print("\n[Step 2] Building transfer learning model...")

# Load pre-trained MobileNetV2
base_model = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights='imagenet')
base_model.trainable = False  # Freeze base model

# Build custom model
inputs = Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = base_model(inputs, training=False)
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.2)(x)
outputs = Dense(len(CLASS_NAMES), activation='softmax')(x)

model = Model(inputs, outputs)

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nModel Architecture:")
print(f"Total params: {model.count_params():,}")

print("\n[Step 3] Phase 1 Training (frozen base, 20 epochs)...")
callbacks = [
    ModelCheckpoint('model/food_model.h5', monitor='accuracy', save_best_only=True, verbose=0),
    ReduceLROnPlateau(monitor='accuracy', factor=0.5, patience=3, min_lr=1e-7, verbose=1)
]

history1 = model.fit(
    data_generator,
    epochs=EPOCHS,
    callbacks=callbacks,
    verbose=1
)

print("\n[Step 4] Phase 2 Fine-tuning (unfreezing top layers, 5 epochs)...")
# Unfreeze top layers
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    data_generator,
    epochs=5,
    callbacks=callbacks,
    verbose=1
)

print("\n" + "=" * 70)
print("✓ Training Complete!")
print("=" * 70)
print(f"Model saved to: model/food_model.h5")
print(f"Final Accuracy: {history2.history['accuracy'][-1]:.2%}")
