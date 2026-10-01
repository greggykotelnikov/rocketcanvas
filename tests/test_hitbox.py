import pytest

from models import db, CarHitbox


@pytest.fixture
def cars(app):
    with app.app_context():
        db.session.add_all([
            CarHitbox(car_name="Octane ZSR", hitbox_class="Octane"),
            CarHitbox(car_name="Octane", hitbox_class="Octane"),
            CarHitbox(car_name="Dominus GT", hitbox_class="Dominus"),
            CarHitbox(car_name="Fennec", hitbox_class="Octane"),
        ])
        db.session.commit()


def lookup(client, name):
    return client.post("/hitbox", data={"car_name": name}).get_data(as_text=True)


def test_exact_match_preferred(auth_client, cars, monkeypatch):
    import app as appmod
    captured = {}
    orig = appmod.render_template

    def spy(template, **ctx):
        captured.update(ctx)
        return orig(template, **ctx)

    monkeypatch.setattr(appmod, "render_template", spy)
    lookup(auth_client, "octane")
    assert captured["result"] == {"car": "Octane", "hitbox": "Octane", "found": True}
    lookup(auth_client, "domin")
    assert captured["result"]["car"] == "Dominus GT"
    for query in ("", "%", "_"):
        lookup(auth_client, query)
        assert captured["result"]["found"] is False, query
