"""
Dev helper: download the latest public replay from ballchasing.com and run
it through the real replay parser to sanity-check heatmap extraction.

Usage (from the project root):
    python scripts/fetch_sample_replay.py            # download + parse
    python scripts/fetch_sample_replay.py test.replay  # parse an existing file

Needs BALLCHASING_API_KEY in .env (download requires a key with download rights).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ballchasing import BASE_URL, HEADERS, download_replay  # noqa: E402
from replay_parser import parse_replay_positions  # noqa: E402
import requests  # noqa: E402


def fetch_latest(dest="test.replay"):
    r = requests.get(f"{BASE_URL}/replays", headers=HEADERS, params={"count": 1}, timeout=15)
    r.raise_for_status()
    rid = r.json()["list"][0]["id"]
    print(f"Downloading replay {rid} -> {dest}")
    with open(dest, "wb") as f:
        f.write(download_replay(rid))
    return dest


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else fetch_latest()
    players = parse_replay_positions(path)
    if not players:
        sys.exit("No positions extracted.")
    for name, positions in players.items():
        print(f"{name}: {len(positions)} positions")
