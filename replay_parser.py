import os
import json
import subprocess  # nosec B404
import requests
import zipfile
import threading

RRROCKET_URL = "https://github.com/nickbabcock/rrrocket/releases/download/v0.11.1/rrrocket-0.11.1-x86_64-pc-windows-msvc.zip"
RRROCKET_DIR = os.path.join(os.path.dirname(__file__), "bin")
RRROCKET_EXE = os.path.join(RRROCKET_DIR, "rrrocket-0.11.1-x86_64-pc-windows-msvc", "rrrocket.exe")
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
        out = subprocess.check_output([RRROCKET_EXE, "-n", replay_path])  # nosec B603
        data = json.loads(out)
    except Exception as e:
        print(f"Error parsing replay: {e}")
        return {}

    if "objects" not in data or "network_frames" not in data:
        return {}

    objects = data["objects"]
    pri_actors = {}      # actor_id -> player name
    car_to_pri = {}      # actor_id (car) -> pri actor_id
    car_positions = {}   # actor_id (car) -> [[x,y], ...]

    for f in data["network_frames"]["frames"]:
        # Register new actors
        if "new_actors" in f:
            for actor in f["new_actors"]:
                obj_name = objects[actor["object_id"]]
                actor_id = actor["actor_id"]
                if "PRI_TA" in obj_name or "PlayerReplicationInfo" in obj_name:
                    pri_actors[actor_id] = "Unknown"
                elif "Car_Default" in obj_name:
                    car_positions[actor_id] = []

        # Update actors
        if "updated_actors" in f:
            for actor in f["updated_actors"]:
                actor_id = actor["actor_id"]
                prop_id = actor.get("object_id")
                if prop_id is None or prop_id >= len(objects): continue
                prop_name = objects[prop_id]
                attr = actor.get("attribute", {})
                
                # Check for PlayerName
                if actor_id in pri_actors:
                    if "PlayerName" in prop_name:
                        val = attr.get("String")
                        if val:
                            pri_actors[actor_id] = val

                # Check for Car linking to PRI
                if actor_id in car_positions:
                    if "PlayerReplicationInfo" in prop_name and ("Pawn" in prop_name or "Car" in prop_name):
                        if "ActiveActor" in attr:
                            if attr["ActiveActor"].get("active"):
                                car_to_pri[actor_id] = attr["ActiveActor"]["actor"]
                        elif "Int" in attr:
                            car_to_pri[actor_id] = attr["Int"]

                    # Check for RigidBody location (property name is ReplicatedRBState)
                    if "ReplicatedRBState" in prop_name:
                        loc = attr.get("RigidBody", {}).get("location", {})
                        if "x" in loc and "y" in loc:
                            # rrrocket gives cm, usually RL maps are ~10240x8192
                            car_positions[actor_id].append([loc["x"], loc["y"]])

    # Build final map
    player_heatmaps = {}
    for car_id, positions in car_positions.items():
        if not positions: continue
        pri_id = car_to_pri.get(car_id)
        if pri_id and pri_id in pri_actors:
            name = pri_actors[pri_id]
            if name != "Unknown":
                player_heatmaps[name] = positions

    return player_heatmaps

if __name__ == '__main__':
    # Test
    res = parse_replay_positions("test.replay")
    for name, pos in res.items():
        print(f"Player {name}: {len(pos)} positions")
