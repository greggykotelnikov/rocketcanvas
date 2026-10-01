import pytest

import ballchasing


@pytest.fixture(autouse=True)
def clear_cache():
    ballchasing._search_cache.clear()
    yield
    ballchasing._search_cache.clear()


def test_search_is_cached_and_returns_copies(monkeypatch):
    calls = []

    def fake(player, count):
        calls.append(player)
        return {"list": [{"id": "r1"}]}

    monkeypatch.setattr(ballchasing, "_search_replays_uncached", fake)
    a = ballchasing.search_replays_by_player("Pilot", count=50)
    a["list"][0]["result"] = "win"           # callers mutate results
    b = ballchasing.search_replays_by_player("pilot", count=50)
    assert calls == ["Pilot"]                # case-insensitive cache hit
    assert "result" not in b["list"][0]      # cache not polluted


def test_cache_expires(monkeypatch):
    calls = []
    monkeypatch.setattr(ballchasing, "_search_replays_uncached",
                        lambda p, c: calls.append(p) or {"list": []})
    clock = [1000.0]
    monkeypatch.setattr(ballchasing.time, "monotonic", lambda: clock[0])
    ballchasing.search_replays_by_player("x", 50)
    clock[0] += ballchasing.SEARCH_CACHE_TTL_S + 1
    ballchasing.search_replays_by_player("x", 50)
    assert len(calls) == 2


def test_errors_are_not_cached(monkeypatch):
    def boom(p, c):
        raise ballchasing.requests.ConnectionError()
    monkeypatch.setattr(ballchasing, "_search_replays_uncached", boom)
    with pytest.raises(ballchasing.requests.ConnectionError):
        ballchasing.search_replays_by_player("x", 50)
    assert ballchasing._search_cache == {}
