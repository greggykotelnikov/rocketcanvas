import requests
import os
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

def search_replays_by_player(player_name, count=10):
    """
    Search replays where a player name matches.
    Returns a list of replay summaries.
    """
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
