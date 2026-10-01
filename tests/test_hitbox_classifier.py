import os

import pytest
from PIL import Image

import hitbox_classifier

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_preprocess_shape_and_range():
    x = hitbox_classifier.preprocess(Image.new("RGBA", (640, 360), (255, 255, 255, 0)))
    assert x.shape == (1, 224, 224, 3)
    assert x.min() >= -1.0 and x.max() <= 1.0


def test_predict_returns_ranked_known_labels():
    if not hitbox_classifier.is_available():
        pytest.skip(hitbox_classifier.unavailable_reason())
    img = Image.open(os.path.join(ROOT, "static", "avatars", "placeholders", "octane.png"))
    preds = hitbox_classifier.predict(img, top_k=3)
    assert len(preds) == 3
    assert {p["hitbox"] for p in preds} <= {"Octane", "Dominus", "Hybrid", "Merc", "Plank", "Breakout"}
    assert preds == sorted(preds, key=lambda p: p["confidence"], reverse=True)
    assert preds[0]["hitbox"] == "Octane"
    assert 0.0 <= preds[-1]["confidence"] <= preds[0]["confidence"] <= 1.0
