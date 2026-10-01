import io
import os
import tempfile

import replay_parser


def upload(client, name="match.replay", data=b"fake"):
    return client.post("/parse-replay", data={"replay_file": (io.BytesIO(data), name)},
                       content_type="multipart/form-data")


def test_rejects_non_replay_extension(auth_client):
    resp = upload(auth_client, name="evil.exe")
    assert resp.status_code == 400


def test_accepts_uppercase_extension(auth_client, monkeypatch):
    monkeypatch.setattr(replay_parser, "parse_replay_positions", lambda p: {"P": [[0, 0]]})
    resp = upload(auth_client, name="MATCH.REPLAY")
    assert resp.status_code == 200 and resp.get_json()["players"] == {"P": [[0, 0]]}


def test_parser_error_is_not_leaked_and_temp_file_removed(auth_client, monkeypatch):
    seen = {}

    def boom(path):
        seen["path"] = path
        raise RuntimeError(r"C:\secret\internal\path exploded")

    monkeypatch.setattr(replay_parser, "parse_replay_positions", boom)
    resp = upload(auth_client)
    assert resp.status_code == 500
    assert "secret" not in resp.get_data(as_text=True)
    assert not os.path.exists(seen["path"])
