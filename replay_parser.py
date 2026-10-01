import hashlib
import io
import json
import os
import platform
import subprocess  # nosec B404
import tarfile
import threading
import zipfile

import requests

RRROCKET_VERSION = "0.11.1"
RRROCKET_DIR = os.path.join(os.path.dirname(__file__), "bin")
RRROCKET_TIMEOUT_S = 60

# Official release assets per (OS, CPU) and the SHA-256 of each archive.
# We execute what we download, so refuse anything that doesn't match.
_RRROCKET_BUILDS = {
    ("windows", "x86_64"): ("x86_64-pc-windows-msvc", ".zip",
                            "0477fe1177d8bfc1bd9929b40679461205507e60f0b46cb1af9d6e4a7231335a"),
    ("linux", "x86_64"):   ("x86_64-unknown-linux-musl", ".tar.gz",
                            "9417a28be27b76020d127e3147a732b92080eb225f0d2a6087d6b046d869b3e8"),
    ("darwin", "x86_64"):  ("x86_64-apple-darwin", ".tar.gz",
                            "f7cf8e2c3e199a42eb6ac1c87a53a979d723ad67e1882214100472e98460959d"),
    ("darwin", "arm64"):   ("aarch64-apple-darwin", ".tar.gz",
                            "8ca9bdad51b39515baac1605ee0e881671c8367459d61c7dfbb95a46276d1fc6"),
}
_ARCH_ALIASES = {"amd64": "x86_64", "x86_64": "x86_64", "arm64": "arm64", "aarch64": "arm64"}


def _current_build():
    """Return (target, archive_ext, sha256) for this machine, or None."""
    system = platform.system().lower()
    arch = _ARCH_ALIASES.get(platform.machine().lower())
    return _RRROCKET_BUILDS.get((system, arch))


def _exe_path(target):
    name = "rrrocket.exe" if target.endswith("windows-msvc") else "rrrocket"
    return os.path.join(RRROCKET_DIR, f"rrrocket-{RRROCKET_VERSION}-{target}", name)


_BUILD = _current_build()
RRROCKET_EXE = _exe_path(_BUILD[0]) if _BUILD else None
_install_lock = threading.Lock()


def ensure_rrrocket():
    """Download the rrrocket binary for this OS/CPU on first use."""
    if _BUILD is None:
        print(f"rrrocket has no build for {platform.system()} {platform.machine()}")
        return False
    target, ext, expected_sha = _BUILD
    with _install_lock:
        if os.path.exists(RRROCKET_EXE):
            return True
        os.makedirs(RRROCKET_DIR, exist_ok=True)
        url = (f"https://github.com/nickbabcock/rrrocket/releases/download/"
               f"v{RRROCKET_VERSION}/rrrocket-{RRROCKET_VERSION}-{target}{ext}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            digest = hashlib.sha256(r.content).hexdigest()
            if digest != expected_sha:
                raise ValueError(f"rrrocket download checksum mismatch: {digest}")
            # Extract only the binary itself, to its expected path, rather
            # than trusting every path inside the archive.
            member = os.path.relpath(RRROCKET_EXE, RRROCKET_DIR).replace(os.sep, "/")
            if ext == ".zip":
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    data = z.read(member)
            else:
                with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as t:
                    data = t.extractfile(member).read()
            os.makedirs(os.path.dirname(RRROCKET_EXE), exist_ok=True)
            with open(RRROCKET_EXE, "wb") as f:
                f.write(data)
            os.chmod(RRROCKET_EXE, 0o755)  # nosec B103 - needs to be executable
            return True
        except Exception as e:
            print(f"Error installing rrrocket: {e}")
            return False

def parse_replay_positions(replay_path):
    """
    Parses a Rocket League .replay file and returns a dict mapping
    PlayerName to a list of [x, y] coordinates.
    """
    if not ensure_rrrocket():
        return {}

    try:
        # Timeout so a malformed/hostile replay can't hang the request worker.
        out = subprocess.check_output(  # nosec B603 - fixed exe path, no shell
            [RRROCKET_EXE, "-n", replay_path],
            timeout=RRROCKET_TIMEOUT_S,
            stderr=subprocess.DEVNULL,
        )
        data = json.loads(out)
    except Exception as e:
        print(f"Error parsing replay: {e}")
        return {}

    return extract_player_positions(data)


def extract_player_positions(data):
    """
    Walk rrrocket's network frames and collect [x, y] car positions per player.

    Actor ids are recycled: when a car is destroyed (goal reset, demolition)
    its id can later be handed to a brand-new car or to an unrelated actor.
    So each car is tracked for its own lifetime (spawn -> delete) and its
    positions are attributed to the player linked to that particular car.
    """
    if "objects" not in data or "network_frames" not in data:
        return {}

    objects = data["objects"]
    pri_names = {}       # PRI actor_id -> player name
    live_cars = {}       # car actor_id -> {"pri": pri actor_id or None, "positions": [[x, y], ...]}
    finished_cars = []   # cars that have been destroyed (or whose id was reused)

    def retire(actor_id):
        car = live_cars.pop(actor_id, None)
        if car is not None:
            finished_cars.append(car)

    for f in data["network_frames"]["frames"]:
        # Deleted actors free their ids; close out any car using that id.
        for actor_id in f.get("deleted_actors", []):
            retire(actor_id)

        # Register new actors
        for actor in f.get("new_actors", []):
            object_id = actor.get("object_id")
            if object_id is None or object_id >= len(objects):
                continue
            obj_name = objects[object_id]
            actor_id = actor["actor_id"]
            retire(actor_id)  # id reuse without an explicit delete
            if "PRI_TA" in obj_name or "PlayerReplicationInfo" in obj_name:
                pri_names[actor_id] = None
            elif "Car_Default" in obj_name:
                live_cars[actor_id] = {"pri": None, "positions": []}

        # Update actors
        for actor in f.get("updated_actors", []):
            actor_id = actor["actor_id"]
            prop_id = actor.get("object_id")
            if prop_id is None or prop_id >= len(objects):
                continue
            prop_name = objects[prop_id]
            attr = actor.get("attribute", {})

            # Check for PlayerName
            if actor_id in pri_names and "PlayerName" in prop_name:
                val = attr.get("String")
                if val:
                    pri_names[actor_id] = val

            car = live_cars.get(actor_id)
            if car is None:
                continue

            # Check for Car linking to PRI. An inactive link (e.g. the car is
            # being demolished) keeps the previous owner.
            if "PlayerReplicationInfo" in prop_name and ("Pawn" in prop_name or "Car" in prop_name):
                if "ActiveActor" in attr:
                    if attr["ActiveActor"].get("active"):
                        car["pri"] = attr["ActiveActor"]["actor"]
                elif "Int" in attr:
                    car["pri"] = attr["Int"]

            # Check for RigidBody location (property name is ReplicatedRBState)
            if "ReplicatedRBState" in prop_name:
                loc = attr.get("RigidBody", {}).get("location", {})
                if "x" in loc and "y" in loc:
                    # rrrocket gives cm, usually RL maps are ~10240x8192
                    car["positions"].append([loc["x"], loc["y"]])

    finished_cars.extend(live_cars.values())

    # Build final map. A player owns many cars over a match (one per
    # kickoff/respawn), so merge all of them.
    player_heatmaps = {}
    for car in finished_cars:
        name = pri_names.get(car["pri"]) if car["pri"] is not None else None
        if name and car["positions"]:
            player_heatmaps.setdefault(name, []).extend(car["positions"])

    return player_heatmaps

if __name__ == '__main__':
    # Test
    res = parse_replay_positions("test.replay")
    for name, pos in res.items():
        print(f"Player {name}: {len(pos)} positions")
