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


def _post(client, data, name="car.png"):
    import io
    return client.post("/hitbox/recognise", data={"image": (io.BytesIO(data), name)},
                       content_type="multipart/form-data")


def test_recognise_endpoint(auth_client):
    if not hitbox_classifier.is_available():
        pytest.skip(hitbox_classifier.unavailable_reason())
    with open(os.path.join(ROOT, "static", "avatars", "placeholders", "octane.png"), "rb") as f:
        resp = _post(auth_client, f.read())
    body = resp.get_json()
    assert resp.status_code == 200 and body["success"]
    assert len(body["predictions"]) == 3
    assert isinstance(body["examples"], list)


def test_recognise_rejects_bad_input(auth_client):
    assert _post(auth_client, b"not an image").status_code == 400
    assert _post(auth_client, b"x", name="car.exe").status_code == 400


def test_recognise_requires_login(client):
    assert _post(client, b"x").status_code == 302


def test_recognise_when_model_unavailable(auth_client, monkeypatch):
    monkeypatch.setattr(hitbox_classifier, "is_available", lambda: False)
    resp = _post(auth_client, b"x")
    assert resp.status_code == 503 and resp.get_json()["success"] is False
