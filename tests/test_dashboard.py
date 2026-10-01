import requests

import app as appmod
from ballchasing import BallchasingConfigError


def make_replay(blue, orange, blue_goals, orange_goals, date="2026-01-01T12:00:00Z", **extra):
    r = {
        "blue": {"goals": blue_goals, "players": [{"name": n} for n in blue]},
        "orange": {"goals": orange_goals, "players": [{"name": n} for n in orange]},
        "date": date, "duration": 300, "map_name": "DFH Stadium", "playlist_id": "ranked-doubles",
    }
    r.update(extra)
    return r


def test_player_team_prefers_exact_match():
    r = make_replay(["Maxwell"], ["max"], 1, 2)
    assert appmod._player_team(r, "max") == "orange"


def test_player_team_substring_fallback_and_missing_name():
    r = make_replay(["xXPilotXx"], [], 0, 0)
    r["orange"]["players"].append({})  # player entry with no name must not crash
    assert appmod._player_team(r, "pilot") == "blue"
    assert appmod._player_team(r, "nobody") is None


def test_dashboard_tags_results(auth_client, monkeypatch):
    replays = [make_replay(["pilot"], ["x"], 3, 1), make_replay(["x"], ["pilot"], 3, 1)]
    monkeypatch.setattr(appmod, "search_replays_by_player", lambda p, count: {"list": replays})
    resp = auth_client.get("/dashboard?player=pilot")
    assert resp.status_code == 200
    assert [r["result"] for r in replays] == ["win", "loss"]


def test_dashboard_reports_missing_api_key(auth_client, monkeypatch):
    def no_key(p, count):
        raise BallchasingConfigError("missing")
    monkeypatch.setattr(appmod, "search_replays_by_player", no_key)
    resp = auth_client.get("/dashboard?player=pilot")
    assert b"Ballchasing API key" in resp.data


def test_analytics_reports_network_error(auth_client, monkeypatch):
    def down(p, count):
        raise requests.ConnectionError("down")
    monkeypatch.setattr(appmod, "search_replays_by_player", down)
    resp = auth_client.get("/analytics?player=pilot")
    assert resp.status_code == 200
    assert b"reach ballchasing.com" in resp.data
