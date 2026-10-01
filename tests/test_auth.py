from models import TwoFactorCode


def register(client):
    return client.post("/register", data={
        "email": "a@example.com", "username": "a", "password": "passw0rd!",
    })


def test_register_redirects_to_verify(client):
    resp = register(client)
    assert resp.status_code == 302
    assert resp.location.endswith("/verify")


def test_correct_code_logs_in(app, client):
    register(client)
    resp = client.post("/verify", data={"code": app.sent_codes[-1]})
    assert resp.location.endswith("/profile")
    assert client.get("/profile").status_code == 200


def test_code_cannot_be_reused(app, client):
    register(client)
    code = app.sent_codes[-1]
    client.post("/verify", data={"code": code})
    client.post("/logout")
    # No pending login any more, so /verify bounces to /login.
    resp = client.post("/verify", data={"code": code})
    assert resp.location.endswith("/login")


def test_lockout_after_five_wrong_codes(app, client):
    register(client)
    code = app.sent_codes[-1]
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(4):
        assert client.post("/verify", data={"code": wrong}).status_code == 200
    resp = client.post("/verify", data={"code": wrong})
    assert resp.location.endswith("/login")
    # The real code is burned too.
    resp = client.post("/verify", data={"code": code})
    assert resp.location.endswith("/login")
    with app.app_context():
        assert TwoFactorCode.query.filter_by(used=False).count() == 0


def test_smtp_failure_does_not_500(app, client, monkeypatch):
    import app as appmod

    def boom(msg):
        raise OSError("smtp down")

    monkeypatch.setattr(appmod.mail, "send", boom)
    resp = register(client)
    assert resp.status_code == 200
    assert b"couldn" in resp.data


def test_protected_pages_require_login(client):
    for path in ("/profile", "/dashboard", "/analytics", "/gallery", "/garage", "/heatmap"):
        resp = client.get(path)
        assert resp.status_code == 302, path
        assert "/login" in resp.location


def test_logout_requires_post(auth_client):
    assert auth_client.get("/logout").status_code == 405
    assert auth_client.get("/profile").status_code == 200
    auth_client.post("/logout")
    assert auth_client.get("/profile").status_code == 302


def test_nav_renders_logout_form(auth_client):
    html = auth_client.get("/profile").get_data(as_text=True)
    assert 'class="nav-logout" method="POST"' in html


def test_login_unknown_email_still_runs_bcrypt(client, monkeypatch):
    import auth
    calls = []
    real = auth.bcrypt.check_password_hash
    monkeypatch.setattr(auth.bcrypt, "check_password_hash",
                        lambda h, p: calls.append(h) or real(h, p))
    resp = client.post("/login", data={"email": "nobody@example.com", "password": "x"})
    assert b"Invalid email or password" in resp.data
    assert len(calls) == 1
