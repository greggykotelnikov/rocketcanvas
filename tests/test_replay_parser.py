from replay_parser import extract_player_positions

OBJECTS = [
    "TAGame.Default__PRI_TA",               # 0
    "Archetypes.Car.Car_Default",           # 1
    "Engine.PlayerReplicationInfo:PlayerName",  # 2
    "Engine.Pawn:PlayerReplicationInfo",    # 3
    "TAGame.RBActor_TA:ReplicatedRBState",  # 4
    "Archetypes.Ball.Ball_Default",         # 5
]


def new(actor_id, object_id):
    return {"actor_id": actor_id, "object_id": object_id}


def name(actor_id, value):
    return {"actor_id": actor_id, "object_id": 2, "attribute": {"String": value}}


def link(car_id, pri_id, active=True):
    return {"actor_id": car_id, "object_id": 3,
            "attribute": {"ActiveActor": {"active": active, "actor": pri_id}}}


def pos(actor_id, x, y):
    return {"actor_id": actor_id, "object_id": 4,
            "attribute": {"RigidBody": {"location": {"x": x, "y": y, "z": 17}}}}


def replay(*frames):
    return {"objects": OBJECTS, "network_frames": {"frames": list(frames)}}


def test_positions_from_all_cars_are_merged():
    data = replay(
        {"new_actors": [new(0, 0), new(5, 1)], "updated_actors": [name(0, "Alice"), link(5, 0), pos(5, 1, 1)]},
        {"deleted_actors": [5]},
        {"new_actors": [new(9, 1)], "updated_actors": [link(9, 0), pos(9, 2, 2)]},
    )
    assert extract_player_positions(data) == {"Alice": [[1, 1], [2, 2]]}


def test_reused_car_id_does_not_drop_earlier_positions():
    data = replay(
        {"new_actors": [new(0, 0), new(5, 1)], "updated_actors": [name(0, "Alice"), link(5, 0), pos(5, 1, 1)]},
        # Same id respawned as a new car without an explicit delete.
        {"new_actors": [new(5, 1)], "updated_actors": [link(5, 0), pos(5, 2, 2)]},
    )
    assert extract_player_positions(data) == {"Alice": [[1, 1], [2, 2]]}


def test_id_reused_by_non_car_is_ignored():
    data = replay(
        {"new_actors": [new(0, 0), new(5, 1)], "updated_actors": [name(0, "Alice"), link(5, 0), pos(5, 1, 1)]},
        {"deleted_actors": [5], "new_actors": [new(5, 5)], "updated_actors": [pos(5, 999, 999)]},
    )
    assert extract_player_positions(data) == {"Alice": [[1, 1]]}


def test_demolition_unlink_keeps_owner_and_actor_id_zero_works():
    data = replay(
        {"new_actors": [new(0, 0), new(3, 1)], "updated_actors": [name(0, "Zero"), link(3, 0), pos(3, 1, 1)]},
        {"updated_actors": [link(3, -1, active=False), pos(3, 2, 2)]},
    )
    assert extract_player_positions(data) == {"Zero": [[1, 1], [2, 2]]}


def test_missing_sections_return_empty():
    assert extract_player_positions({}) == {}


def test_build_selection_per_platform(monkeypatch):
    import replay_parser

    def build_for(system, machine):
        monkeypatch.setattr(replay_parser.platform, "system", lambda: system)
        monkeypatch.setattr(replay_parser.platform, "machine", lambda: machine)
        b = replay_parser._current_build()
        return b and b[0]

    assert build_for("Windows", "AMD64") == "x86_64-pc-windows-msvc"
    assert build_for("Linux", "x86_64") == "x86_64-unknown-linux-musl"
    assert build_for("Darwin", "arm64") == "aarch64-apple-darwin"
    assert build_for("Darwin", "x86_64") == "x86_64-apple-darwin"
    assert build_for("Linux", "aarch64") is None
