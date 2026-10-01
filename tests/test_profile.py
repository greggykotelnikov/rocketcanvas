from models import User


def get_user(app):
    with app.app_context():
        return User.query.filter_by(username="pilot").first()


def test_profile_update_valid(app, auth_client):
    auth_client.post("/profile/update", data={
        "rl_username": "Pilot", "rank": "Champion II", "platform": "Steam", "bio": "hi",
    })
    u = get_user(app)
    assert (u.rl_username, u.rank, u.platform, u.bio) == ("Pilot", "Champion II", "Steam", "hi")


def test_profile_update_rejects_unknown_values(app, auth_client):
    auth_client.post("/profile/update", data={
        "rl_username": "x" * 500, "rank": "Galaxy Brain", "platform": "<b>PC</b>", "bio": "b" * 1000,
    })
    u = get_user(app)
    assert len(u.rl_username) == 80
    assert u.rank is None and u.platform is None
    assert len(u.bio) == 300


def test_profile_page_lists_ranks(auth_client):
    html = auth_client.get("/profile").data
    assert b"Supersonic Legend" in html and b"Grand Champion III" in html and b"Epic Games" in html
