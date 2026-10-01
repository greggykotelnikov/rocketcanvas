def test_security_headers_present(client):
    resp = client.get("/login")
    h = resp.headers
    assert "nonce-" in h["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in h["Content-Security-Policy"]
    assert h["X-Frame-Options"] == "DENY"
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-XSS-Protection"] == "0"
    assert "Strict-Transport-Security" not in h  # plain-HTTP test client
    assert "max-age=" in client.get("/login", base_url="https://localhost").headers["Strict-Transport-Security"]
    assert "Server" not in h


def test_csp_nonce_changes_per_request(client):
    a = client.get("/login").headers["Content-Security-Policy"]
    b = client.get("/login").headers["Content-Security-Policy"]
    assert a != b
