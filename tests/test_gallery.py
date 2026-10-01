import io
import os

import app as appmod
from models import db, CarDesign, User
from tests.test_uploads import image_bytes


def upload(client, title="Mine"):
    client.post("/gallery/upload", data={"title": title, "design_image": (image_bytes("PNG", "RGB"), "c.png")},
                content_type="multipart/form-data")


def test_owner_can_delete_design(app, auth_client):
    upload(auth_client)
    with app.app_context():
        d = CarDesign.query.one()
        path = os.path.join(appmod.DESIGN_UPLOAD_DIR, d.image_filename)
        did = d.id
    assert os.path.exists(path)
    assert b"Delete" in auth_client.get("/gallery").data
    resp = auth_client.post(f"/gallery/{did}/delete", follow_redirects=True)
    assert b"Design deleted" in resp.data
    assert not os.path.exists(path)
    with app.app_context():
        assert CarDesign.query.count() == 0


def test_cannot_delete_someone_elses_design(app, auth_client):
    with app.app_context():
        other = User(email="o@example.com", username="other", password_hash="x")
        db.session.add(other)
        db.session.commit()
        d = CarDesign(user_id=other.id, title="Theirs", image_filename="nope.png")
        db.session.add(d)
        db.session.commit()
        did = d.id
    html = auth_client.get("/gallery").get_data(as_text=True)
    assert "Theirs" in html and f"/gallery/{did}/delete" not in html
    assert auth_client.post(f"/gallery/{did}/delete").status_code == 403
    assert auth_client.post("/gallery/99999/delete").status_code == 404
    with app.app_context():
        assert CarDesign.query.count() == 1
