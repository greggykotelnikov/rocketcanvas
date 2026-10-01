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
