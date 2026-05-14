"""
train_hitbox_model.py
=====================
Retrain the RocketCanvas hitbox classifier from scratch using your
hitbox_images/ dataset. Produces ml/keras_model.h5 compatible with
the existing _load_hitbox_model_rebuilt() loader in app.py.

Usage:
    python train_hitbox_model.py

Requirements (all already in venv311):
    tensorflow-cpu >= 2.16, numpy, Pillow
"""

import os
import pathlib

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"   # suppress info/warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.applications import MobileNetV2

# ── Config ─────────────────────────────────────────────────────────────
IMG_SIZE     = 224          # MobileNetV2 expects 224×224
BATCH_SIZE   = 16
EPOCHS_HEAD  = 15           # Train only the new head first
EPOCHS_FINE  = 20           # Then fine-tune top layers of backbone
LEARNING_RATE_HEAD = 1e-3
LEARNING_RATE_FINE = 1e-5
DATA_DIR     = pathlib.Path("hitbox_images")
OUTPUT_PATH  = pathlib.Path("ml/keras_model.h5")
SEED         = 42

# ── Labels (must match labels.txt order) ───────────────────────────────
CLASS_NAMES = ["octane", "dominus", "hybrid", "merc", "plank", "breakout"]
NUM_CLASSES = len(CLASS_NAMES)

print(f"TensorFlow {tf.__version__}")
print(f"Dataset: {DATA_DIR.resolve()}")
print(f"Output:  {OUTPUT_PATH.resolve()}")


# ── Load dataset ───────────────────────────────────────────────────────
def make_dataset(validation_split=0.2):
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASS_NAMES,
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        image_size=(IMG_SIZE, IMG_SIZE),
        shuffle=True,
        seed=SEED,
        validation_split=validation_split,
        subset="training",
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASS_NAMES,
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        image_size=(IMG_SIZE, IMG_SIZE),
        shuffle=False,
        seed=SEED,
        validation_split=validation_split,
        subset="validation",
    )
    return train_ds, val_ds


train_ds, val_ds = make_dataset()

# Print class counts for transparency
all_files = list(DATA_DIR.glob("*/*.png")) + list(DATA_DIR.glob("*/*.jpg")) + list(DATA_DIR.glob("*/*.jpeg"))
from collections import Counter
counts = Counter(f.parent.name for f in all_files)
print("\nClass counts:")
for c in CLASS_NAMES:
    print(f"  {c}: {counts.get(c, 0)}")

# ── Compute class weights to handle imbalance ──────────────────────────
total = sum(counts.values())
class_weight = {}
for i, c in enumerate(CLASS_NAMES):
    n = counts.get(c, 1)
    # weight = total / (num_classes * count)
    class_weight[i] = total / (NUM_CLASSES * n)
print("\nClass weights:", {CLASS_NAMES[i]: round(w, 2) for i, w in class_weight.items()})


# ── Preprocessing + augmentation ───────────────────────────────────────
# MobileNetV2 expects pixel values in [-1, 1]
normalization = layers.Rescaling(1.0 / 127.5, offset=-1.0)

augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.15),
    layers.RandomBrightness(0.2),
    layers.RandomContrast(0.2),
], name="augmentation")

AUTOTUNE = tf.data.AUTOTUNE

def preprocess_train(images, labels):
    images = augmentation(images, training=True)
    images = normalization(images)
    return images, labels

def preprocess_val(images, labels):
    images = normalization(images)
    return images, labels

train_ds = train_ds.map(preprocess_train, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
val_ds   = val_ds.map(preprocess_val,   num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)


# ── Build model ────────────────────────────────────────────────────────
print("\nBuilding model...")
backbone = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights="imagenet",
)
backbone.trainable = False   # Freeze backbone initially

inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = backbone(inputs, training=False)
x = layers.GlobalAveragePooling2D(name="gap")(x)
x = layers.Dropout(0.3)(x)
x = layers.Dense(128, activation="relu", name="dense_head")(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(NUM_CLASSES, activation="softmax", name="predictions")(x)
model = tf.keras.Model(inputs, outputs)

model.summary(line_length=80)


# ── Phase 1: Train head only ───────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Phase 1: Training head for {EPOCHS_HEAD} epochs")
print(f"{'='*60}")

model.compile(
    optimizer=tf.keras.optimizers.Adam(LEARNING_RATE_HEAD),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

cb_list = [
    callbacks.EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True),
    callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
]

history1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_HEAD,
    class_weight=class_weight,
    callbacks=cb_list,
)


# ── Phase 2: Fine-tune top backbone layers ─────────────────────────────
print(f"\n{'='*60}")
print(f"Phase 2: Fine-tuning top backbone layers for {EPOCHS_FINE} epochs")
print(f"{'='*60}")

# Unfreeze last 30 layers of backbone
backbone.trainable = True
for layer in backbone.layers[:-30]:
    layer.trainable = False

trainable_count = sum(1 for l in backbone.layers if l.trainable)
print(f"Backbone trainable layers: {trainable_count}/{len(backbone.layers)}")

model.compile(
    optimizer=tf.keras.optimizers.Adam(LEARNING_RATE_FINE),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

cb_list2 = [
    callbacks.EarlyStopping(monitor="val_accuracy", patience=7, restore_best_weights=True),
    callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, verbose=1),
    callbacks.ModelCheckpoint(
        str(OUTPUT_PATH),
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1,
    ),
]

history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_FINE,
    class_weight=class_weight,
    callbacks=cb_list2,
    initial_epoch=len(history1.history["loss"]),
)


# ── Save final model ───────────────────────────────────────────────────
OUTPUT_PATH.parent.mkdir(exist_ok=True)
model.save(str(OUTPUT_PATH))
print(f"\nModel saved to {OUTPUT_PATH}")

# ── Quick eval ────────────────────────────────────────────────────────
loss, acc = model.evaluate(val_ds, verbose=0)
print(f"Final validation accuracy: {acc*100:.1f}%")
print(f"Final validation loss:     {loss:.4f}")

# ── Per-class accuracy ─────────────────────────────────────────────────
print("\nPer-class accuracy on validation set:")
y_true, y_pred = [], []
for images, labels in val_ds:
    preds = model.predict(images, verbose=0)
    y_pred.extend(np.argmax(preds, axis=1))
    y_true.extend(np.argmax(labels.numpy(), axis=1))

y_true, y_pred = np.array(y_true), np.array(y_pred)
for i, name in enumerate(CLASS_NAMES):
    mask = y_true == i
    if mask.sum() > 0:
        class_acc = (y_pred[mask] == i).mean() * 100
        print(f"  {name:12s}: {class_acc:.1f}%  ({mask.sum()} samples)")
    else:
        print(f"  {name:12s}: no validation samples")
