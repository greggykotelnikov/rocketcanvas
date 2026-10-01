"""
Image -> hitbox class prediction using the Teachable Machine model.

The model (MobileNetV2 features + dense head, 224x224 RGB input scaled to
[-1, 1]) was exported to ONNX by scripts/convert_model_to_onnx.py and is
run with onnxruntime. Everything is loaded lazily on first use so the app
starts fine, and the rest of the site keeps working, if onnxruntime is
not installed.
"""
import os
import threading

from PIL import Image

ML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml")
MODEL_PATH = os.path.join(ML_DIR, "hitbox_classifier.onnx")
LABELS_PATH = os.path.join(ML_DIR, "labels.txt")
INPUT_SIZE = 224

_session = None
_labels = None
_load_error = None
_lock = threading.Lock()


def _load_labels():
    # labels.txt lines look like "0 Octane"
    with open(LABELS_PATH, encoding="utf-8") as f:
        return [line.strip().split(" ", 1)[1] for line in f if line.strip()]


def _load():
    """Load the ONNX session once; remember the failure reason if any."""
    global _session, _labels, _load_error
    with _lock:
        if _session is not None or _load_error is not None:
            return
        try:
            import onnxruntime as ort
            _labels = _load_labels()
            _session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
        except Exception as e:  # missing package, missing/corrupt model file
            _load_error = f"{type(e).__name__}: {e}"


def is_available():
    _load()
    return _session is not None


def unavailable_reason():
    _load()
    return _load_error


def preprocess(img):
    """Centre-crop to a square, resize to 224x224, scale to [-1, 1] (NHWC)."""
    import numpy as np

    img = img.convert("RGB")
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((INPUT_SIZE, INPUT_SIZE), Image.LANCZOS)
    x = np.asarray(img, dtype=np.float32) / 127.5 - 1.0
    return x[None, ...]


def predict(img, top_k=3):
    """Return the top_k [{"hitbox": str, "confidence": float}] for a PIL image."""
    if not is_available():
        raise RuntimeError(f"hitbox classifier unavailable ({_load_error})")
    x = preprocess(img)
    probs = _session.run(None, {_session.get_inputs()[0].name: x})[0][0]
    ranked = sorted(zip(_labels, probs), key=lambda p: p[1], reverse=True)[:top_k]
    return [{"hitbox": label, "confidence": round(float(p), 4)} for label, p in ranked]
