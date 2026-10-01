import os
import json
import subprocess  # nosec B404
import requests
import zipfile
import threading

RRROCKET_URL = "https://github.com/nickbabcock/rrrocket/releases/download/v0.11.1/rrrocket-0.11.1-x86_64-pc-windows-msvc.zip"
RRROCKET_DIR = os.path.join(os.path.dirname(__file__), "bin")
RRROCKET_EXE = os.path.join(RRROCKET_DIR, "rrrocket-0.11.1-x86_64-pc-windows-msvc", "rrrocket.exe")
RRROCKET_TIMEOUT_S = 60
_install_lock = threading.Lock()

def ensure_rrrocket():
    with _install_lock:
        if os.path.exists(RRROCKET_EXE):
            return True
        os.makedirs(RRROCKET_DIR, exist_ok=True)
        zip_path = os.path.join(RRROCKET_DIR, "rrrocket.zip")
        try:
            r = requests.get(RRROCKET_URL, timeout=30)
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                f.write(r.content)
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(RRROCKET_DIR)
            os.remove(zip_path)
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
