import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BALLCHASING_API_KEY")
BASE_URL = "https://ballchasing.com/api"

HEADERS = {
    "Authorization": API_KEY
}

def test_connection():
    """Ping the API to verify the key works."""
    r = requests.get(f"{BASE_URL}/", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def search_replays_by_player(player_name, count=10):
    """
    Search replays where a player name matches.
    Returns a list of replay summaries.
    """
    params = {
        "player-name": player_name,
        "count": count,
        "sort-by": "replay-date",
        "sort-dir": "desc"
    }
    r = requests.get(f"{BASE_URL}/replays", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()  # has 'list' key with replay objects