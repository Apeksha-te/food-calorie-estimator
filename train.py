import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models

DATASET_DIR = "dataset"
IMG_SIZE = 224
BATCH = 32
CLASSES = ["apple", "banana", "biryani", "burger", "dosa", "idli",
           "pasta", "pizza", "rice", "samosa", "sandwich"]

for c in CLASSES:
    p = os.path.join(DATASET_DIR, c)
    if not os.path.isdir(p):
        raise SystemExit(f"Missing folder: {p}")
    n = len(os.listdir(p))
    print(f"{c:10s}: {n} images")
    if n < 50:
        print(f"  WARNING: {c} has few images; aim for 200+")

common = dict(directory=DATASET_DIR, labels="inferred", label_mode="categorical",
              class_names=CLASSES, image_size=(IMG_SIZE, IMG_SIZE),
              batch_size=BATCH, validation_split=0.2, seed=42)
train_ds = tf.keras.utils.image_dataset_from_directory(subset="training", **common)
val_ds = tf.keras.utils.image_dataset_from_directory(subset="validation", **common)
train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

augment = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.15),
    layers.RandomContrast(0.15),
])

base = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights="imagenet")
base.trainable = False

inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = augment(inputs)
x = layers.Rescaling(1 / 127.5, offset=-1)(x)
x = base(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(CLASSES), activation="softmax")(x)
model = models.Model(inputs, outputs)

cb = [tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True,
                                       monitor="val_accuracy")]

model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
              loss="categorical_crossentropy", metrics=["accuracy"])
model.fit(train_ds, validation_data=val_ds, epochs=10, callbacks=cb)

base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False
model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
              loss="categorical_crossentropy", metrics=["accuracy"])
model.fit(train_ds, validation_data=val_ds, epochs=15, callbacks=cb)

loss, acc = model.evaluate(val_ds)
print(f"\nFinal validation accuracy: {acc * 100:.1f}%")

os.makedirs("model", exist_ok=True)
model.save(os.path.join("model", "food_model.h5"))
with open(os.path.join("model", "labels.json"), "w") as f:
    json.dump(CLASSES, f)
print("Saved model/food_model.h5 and model/labels.json")