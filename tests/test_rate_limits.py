import io

import app as appmod
import replay_parser


def test_parse_replay_is_rate_limited(auth_client, monkeypatch):
    monkeypatch.setattr(replay_parser, "parse_replay_positions", lambda p: {"P": [[0, 0]]})
    appmod.limiter.reset()
    appmod.limiter.enabled = True
    try:
        codes = [
            auth_client.post("/parse-replay",
                             data={"replay_file": (io.BytesIO(b"x"), "a.replay")},
                             content_type="multipart/form-data").status_code
            for _ in range(5)
        ]
        last = auth_client.post("/parse-replay",
                                data={"replay_file": (io.BytesIO(b"x"), "a.replay")},
                                content_type="multipart/form-data")
        codes.append(last.status_code)
    finally:
        appmod.limiter.enabled = False
        appmod.limiter.reset()
    assert codes == [200] * 5 + [429]
    assert last.get_json()["success"] is False


def test_login_rate_limit_shows_message(client):
    appmod.limiter.reset()
    appmod.limiter.enabled = True
    try:
        for _ in range(5):
            client.post("/login", data={"email": "x@example.com", "password": "nope"})
        resp = client.post("/login", data={"email": "x@example.com", "password": "nope"})
    finally:
        appmod.limiter.enabled = False
        appmod.limiter.reset()
    assert resp.status_code == 429
    assert b"Too many requests" in resp.data
