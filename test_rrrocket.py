import os
import requests
import zipfile
import subprocess  # nosec B404
import json

RRROCKET_URL = "https://github.com/nickbabcock/rrrocket/releases/download/v0.11.1/rrrocket-0.11.1-x86_64-pc-windows-msvc.zip"
RRROCKET_DIR = os.path.join(os.path.dirname(__file__), "bin")
RRROCKET_EXE = os.path.join(RRROCKET_DIR, "rrrocket-0.11.1-x86_64-pc-windows-msvc", "rrrocket.exe")

def install_rrrocket():
    if os.path.exists(RRROCKET_EXE):
        return
    os.makedirs(RRROCKET_DIR, exist_ok=True)
    zip_path = os.path.join(RRROCKET_DIR, "rrrocket.zip")
    print("Downloading rrrocket...")
    r = requests.get(RRROCKET_URL, timeout=30)
    with open(zip_path, "wb") as f:
        f.write(r.content)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(RRROCKET_DIR)
    os.remove(zip_path)
    print("rrrocket installed.")

if __name__ == "__main__":
    install_rrrocket()
    
    # Download a sample replay to test
    from dotenv import load_dotenv
    load_dotenv()
    headers = {"Authorization": os.getenv("BALLCHASING_API_KEY")}
    r = requests.get("https://ballchasing.com/api/replays?count=1", headers=headers, timeout=15)
    rid = r.json()["list"][0]["id"]
    print(f"Testing replay: {rid}")
    
    r2 = requests.get(f"https://ballchasing.com/api/replays/{rid}/file", headers=headers, timeout=15)
    test_replay = "test.replay"
    with open(test_replay, "wb") as f:
        f.write(r2.content)
        
    # Run rrrocket with network parsing (-n) to see if we can get rigid body state
    # Wait, rrrocket without flags outputs the header and network data as JSON
    print("Parsing with rrrocket...")
    out = subprocess.check_output([RRROCKET_EXE, "-n", test_replay])  # nosec B603
    data = json.loads(out)
    
    if "objects" in data and "network_frames" in data:
        objects = data["objects"]
        pri_actors = {} # actor_id -> player name
        car_to_pri = {} # actor_id (car) -> pri actor_id
        car_positions = {} # actor_id (car) -> [(x,y), ...]
        
        for f in data["network_frames"]["frames"]:
            if "new_actors" in f:
                for actor in f["new_actors"]:
                    obj_name = objects[actor["object_id"]]
                    if "PlayerReplicationInfo" in obj_name:
                        pri_actors[actor["actor_id"]] = "Unknown"
                    elif "Car" in obj_name:
                        car_positions[actor["actor_id"]] = []
                        
            if "updated_actors" in f:
                for actor in f["updated_actors"]:
                    attr = actor.get("attribute", {})
                    if "String" in attr and actor["actor_id"] in pri_actors:
                        # Engine.PlayerReplicationInfo_TA:PlayerName is usually a String
                        pri_actors[actor["actor_id"]] = attr["String"]
                    
                    if "ActiveActor" in attr and actor["actor_id"] in car_positions:
                        # Sometimes Engine.Pawn_TA:PlayerReplicationInfo comes as ActiveActor
                        if attr["ActiveActor"].get("active"):
                            car_to_pri[actor["actor_id"]] = attr["ActiveActor"]["actor"]
                            
                    if "RigidBody" in attr and actor["actor_id"] in car_positions:
                        loc = attr["RigidBody"].get("location", {})
                        if "x" in loc and "y" in loc:
                            car_positions[actor["actor_id"]].append((loc["x"], loc["y"]))
                            
        pri_count = 0
        car_count = 0
        print("Number of objects:", len(objects))
        print("Sample objects:", objects[:10])
        # Find if any object has PRI
        for i, o in enumerate(objects):
            if "PlayerName" in o:
                print(f"Object {i} is PlayerName:", o)
            if "ReplicationInfo" in o and "Player" in o:
                print(f"Object {i} is PRI:", o)
