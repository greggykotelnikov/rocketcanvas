import copy
import os
import threading
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BALLCHASING_API_KEY")
BASE_URL = "https://ballchasing.com/api"

HEADERS = {
    "Authorization": API_KEY
}


class BallchasingConfigError(RuntimeError):
    """Raised when no API key is configured."""


def _require_key():
    # requests silently drops headers whose value is None, so without this
    # check every call goes out unauthenticated and fails with a 401.
    if not API_KEY:
        raise BallchasingConfigError("BALLCHASING_API_KEY is not set")

def test_connection():
    """Ping the API to verify the key works."""
    _require_key()
    r = requests.get(f"{BASE_URL}/", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

SEARCH_CACHE_TTL_S = 300
_SEARCH_CACHE_MAX = 256
_search_cache = {}            # (player_lower, count) -> (expires_at, json)
_search_cache_lock = threading.Lock()


def search_replays_by_player(player_name, count=10):
    """
    Search replays where a player name matches.
    Returns a list of replay summaries.

    Results are cached for a few minutes: the dashboard and analytics pages
    usually search the same player back to back, and each uncached call
    costs ~1s plus Ballchasing API quota. Callers get a deep copy, since
    they annotate the replay dicts in place.
    """
    key = (player_name.lower(), count)
    now = time.monotonic()
    with _search_cache_lock:
        hit = _search_cache.get(key)
        if hit and hit[0] > now:
            return copy.deepcopy(hit[1])

    data = _search_replays_uncached(player_name, count)

    with _search_cache_lock:
        if len(_search_cache) >= _SEARCH_CACHE_MAX:
            # Drop expired entries first, then the oldest if still full.
            for k in [k for k, (exp, _) in _search_cache.items() if exp <= now]:
                del _search_cache[k]
            if len(_search_cache) >= _SEARCH_CACHE_MAX:
                del _search_cache[min(_search_cache, key=lambda k: _search_cache[k][0])]
        _search_cache[key] = (now + SEARCH_CACHE_TTL_S, data)
    return copy.deepcopy(data)


def _search_replays_uncached(player_name, count):
    _require_key()
    params = {
        "player-name": player_name,
        "count": count,
        "sort-by": "replay-date",
        "sort-dir": "desc"
    }
    r = requests.get(f"{BASE_URL}/replays", headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()  # has 'list' key with replay objects

def get_replay_detail(replay_id):
    _require_key()
    r = requests.get(f"{BASE_URL}/replays/{replay_id}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

def download_replay(replay_id):
    """
    Downloads the binary .replay file from Ballchasing API.
    Returns the binary content (bytes).
    Note: Requires a Patreon-linked API key with download permissions.
    """
    _require_key()
    r = requests.get(f"{BASE_URL}/replays/{replay_id}/file", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.content
