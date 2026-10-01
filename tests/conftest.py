import os
import re
import sys

import pytest

# Configure the app for tests before it is imported: in-memory DB, fixed key.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as appmod  # noqa: E402
from models import db, User, TwoFactorCode, CarDesign  # noqa: E402


@pytest.fixture
def app(monkeypatch):
    flask_app = appmod.app
    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    appmod.limiter.enabled = False

    sent_codes = []

    def fake_send(msg):
        sent_codes.append(re.search(r"code is: (\d{6})", msg.body).group(1))

    monkeypatch.setattr(appmod.mail, "send", fake_send)
    flask_app.sent_codes = sent_codes

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """A client that has registered and completed 2FA."""
    client.post("/register", data={
        "email": "pilot@example.com",
        "username": "pilot",
        "password": "s3cret-pass!",
    })
    resp = client.post("/verify", data={"code": app.sent_codes[-1]})
    assert resp.status_code == 302 and resp.location.endswith("/profile")
    return client
