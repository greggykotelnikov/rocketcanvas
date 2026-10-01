import io
import os

from PIL import Image

import app as appmod
from models import User


def image_bytes(fmt="PNG", mode="RGBA", size=(300, 200)):
    buf = io.BytesIO()
    Image.new(mode, size, (255, 0, 0, 128) if mode == "RGBA" else (255, 0, 0)).save(buf, format=fmt)
    buf.seek(0)
    return buf


def current_avatar(app):
    with app.app_context():
        return User.query.filter_by(username="pilot").first().avatar_url


def test_avatar_upload_is_png_with_unique_name(app, auth_client):
    auth_client.post("/profile/avatar", data={"avatar": (image_bytes(), "me.png")},
                     content_type="multipart/form-data")
    first = current_avatar(app)
    assert first and first.endswith(".png")
    first_path = os.path.join(appmod.AVATAR_UPLOAD_DIR, first)
    assert os.path.exists(first_path)

    auth_client.post("/profile/avatar", data={"avatar": (image_bytes(), "me.png")},
                     content_type="multipart/form-data")
    second = current_avatar(app)
    assert second != first
    assert not os.path.exists(first_path), "old avatar should be deleted"
    os.remove(os.path.join(appmod.AVATAR_UPLOAD_DIR, second))


def test_rgba_image_named_jpg_is_accepted(app, auth_client):
    resp = auth_client.post("/profile/avatar", data={"avatar": (image_bytes("PNG", "RGBA"), "me.jpg")},
                            content_type="multipart/form-data", follow_redirects=True)
    assert b"Avatar updated" in resp.data
    os.remove(os.path.join(appmod.AVATAR_UPLOAD_DIR, current_avatar(app)))


def test_non_image_avatar_rejected(app, auth_client):
    resp = auth_client.post("/profile/avatar",
                            data={"avatar": (io.BytesIO(b"<script>alert(1)</script>"), "evil.png")},
                            content_type="multipart/form-data", follow_redirects=True)
    assert b"Could not process image" in resp.data
    assert current_avatar(app) is None


def test_gallery_upload_sanitises_fields(app, auth_client):
    from models import CarDesign
    resp = auth_client.post("/gallery/upload", data={
        "title": "T" * 500,
        "overlay_title": "O" * 500,
        "card_template": "legendary\" onmouseover=\"alert(1)",
        "design_image": (image_bytes("PNG", "RGB"), "car.gif"),
    }, content_type="multipart/form-data", follow_redirects=True)
    assert b"Design uploaded" in resp.data
    assert b"flash celebrate" in resp.data
    with app.app_context():
        design = CarDesign.query.one()
        assert len(design.title) == 150
        assert len(design.overlay_title) == 100
        assert design.card_template == "legendary"
        assert design.image_filename.endswith(".png")
        os.remove(os.path.join(appmod.DESIGN_UPLOAD_DIR, design.image_filename))


def test_gallery_upload_rejects_non_image(app, auth_client):
    resp = auth_client.post("/gallery/upload", data={
        "title": "x",
        "design_image": (io.BytesIO(b"GIF89a not really"), "car.gif"),
    }, content_type="multipart/form-data", follow_redirects=True)
    assert b"Could not process image" in resp.data


def test_huge_dimension_image_rejected(app, auth_client):
    # 6000x6000 single-colour PNG compresses to a tiny file but would
    # decode to ~100 MB of RGBA.
    buf = io.BytesIO()
    Image.new("1", (6000, 6000)).save(buf, format="PNG")
    buf.seek(0)
    assert len(buf.getvalue()) < 200_000
    resp = auth_client.post("/profile/avatar", data={"avatar": (buf, "bomb.png")},
                            content_type="multipart/form-data", follow_redirects=True)
    assert b"Could not process image" in resp.data
