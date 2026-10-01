import app as appmod
from tests.test_dashboard import make_replay


def tagged(replays, player="pilot"):
    for r in replays:
        team = appmod._player_team(r, player)
        b, o = appmod._team_goals(r)
        r["player_team"] = team
        r["result"] = "unknown" if team is None else (
            "win" if (b > o) == (team == "blue") else "loss")
    return replays


def newest_first(*results):
    """Build replays newest-first (as Ballchasing returns them) from W/L chars."""
    return tagged([
        make_replay(["pilot"], ["x"], 2 if c == "W" else 0, 1)
        for c in results
    ])


def test_time_series_are_oldest_to_newest():
    # Newest-first: W, W, L, L, L  => chronologically L, L, L, W, W
    stats = appmod._compute_analytics(newest_first("W", "W", "L", "L", "L"), "pilot")
    assert stats["cumulative_wins"] == [0, 0, 0, 1, 2]
    assert stats["diff_values"] == [-1, -1, -1, 1, 1]
    assert stats["current_streak"] == 2 and stats["current_streak_type"] == "win"
    assert stats["best_win_streak"] == 2 and stats["worst_loss_streak"] == 3


def test_rolling_win_rate_window():
    stats = appmod._compute_analytics(newest_first("W", "W", "W", "W", "W", "L"), "pilot")
    # Chronological: L W W W W W
    assert stats["wr_trend_values"] == [80.0, 100.0]


def test_null_duration_and_unknown_team_are_tolerated(auth_client, monkeypatch):
    replays = [
        make_replay(["pilot"], ["x"], 3, 0, duration=None),
        make_replay(["a"], ["b"], 9, 0),  # player not found -> unknown
    ]
    monkeypatch.setattr(appmod, "search_replays_by_player", lambda p, count: {"list": replays})
    assert auth_client.get("/dashboard?player=pilot").status_code == 200
    assert auth_client.get("/analytics?player=pilot").status_code == 200
    stats = appmod._compute_analytics(replays, "pilot")
    assert stats["avg_diff"] == 3.0  # unknown game not averaged in as 0


def test_playlists_sorted_by_frequency():
    replays = [make_replay(["pilot"], [], 1, 0, playlist_id=p)
               for p in ["a", "b", "c", "d", "e", "f", "g", "g", "g"]]
    stats = appmod._compute_analytics(tagged(replays), "pilot")
    assert stats["playlist_labels"][0] == "g"
    assert stats["playlist_values"][0] == 3
