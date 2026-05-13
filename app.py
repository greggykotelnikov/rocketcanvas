import os
import secrets as _secrets
from collections import defaultdict
from datetime import datetime

from flask import Flask, flash, request, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from PIL import Image

from models import db, User
from auth import register_auth_routes, bcrypt as auth_bcrypt
from ballchasing import search_replays_by_player
from models import CarHitbox

load_dotenv()

# ── App factory ────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"]                  = os.getenv("SECRET_KEY", _secrets.token_hex(32))
app.config["SQLALCHEMY_DATABASE_URI"]     = "sqlite:///rocketcanvas.db"
app.config["MAIL_SERVER"]                 = "smtp.gmail.com"
app.config["MAIL_PORT"]                   = 587
app.config["MAIL_USE_TLS"]                = True
app.config["MAIL_USERNAME"]               = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"]               = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"]         = os.getenv("MAIL_DEFAULT_SENDER")
app.config["SESSION_COOKIE_SAMESITE"]     = "Lax"
app.config["SESSION_COOKIE_SECURE"]       = os.getenv("FLASK_ENV", "development") == "production"
app.config["SESSION_COOKIE_HTTPONLY"]     = True
app.config["WTF_CSRF_ENABLED"]            = True
app.config["MAX_CONTENT_LENGTH"]          = 4 * 1024 * 1024   # 4 MB avatar limit

AVATAR_UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads", "avatars")
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

# ── Extensions ─────────────────────────────────────────────────────────
db.init_app(app)
auth_bcrypt.init_app(app)
mail = Mail(app)
csrf = CSRFProtect(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["300 per day", "60 per hour"],
    storage_uri="memory://",
)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

register_auth_routes(app, mail)

# ── DB init + column migration shim ────────────────────────────────────
with app.app_context():
    db.create_all()
    # Add new columns if upgrading from older schema
    from sqlalchemy import text
    with db.engine.connect() as conn:
        for col, defn in [("rank", "VARCHAR(50)"), ("bio", "VARCHAR(300)"), ("avatar_url", "VARCHAR(200)")]:
            try:
                conn.execute(text(f"ALTER TABLE user ADD COLUMN {col} {defn}"))
                conn.commit()
            except Exception:
                pass  # Column already exists


# ── Security headers ───────────────────────────────────────────────────
@app.before_request
def generate_nonce():
    from flask import g
    import secrets
    g.nonce = secrets.token_urlsafe(16)

@app.context_processor
def inject_nonce():
    from flask import g
    return dict(nonce=getattr(g, 'nonce', ''))

@app.after_request
def add_security_headers(response):
    from flask import g
    nonce = getattr(g, 'nonce', '')
    response.headers["X-Frame-Options"]           = "DENY"
    response.headers["X-Content-Type-Options"]    = "nosniff"
    response.headers["X-XSS-Protection"]          = "1; mode=block"
    response.headers["Referrer-Policy"]            = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"]         = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"]   = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        f"style-src 'self' 'nonce-{nonce}' fonts.googleapis.com; "
        "font-src fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    response.headers.pop("Server", None)
    return response


# ── Helper ─────────────────────────────────────────────────────────────
def allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXT


# ── Routes ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    current_user.rl_username = request.form.get("rl_username", "").strip() or None
    current_user.rank        = request.form.get("rank", "").strip() or None
    current_user.bio         = request.form.get("bio", "").strip()[:300] or None
    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/avatar", methods=["POST"])
@login_required
def update_avatar():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("profile"))
    if not allowed_image(file.filename):
        flash("Only image files are allowed (PNG, JPG, WEBP).", "error")
        return redirect(url_for("profile"))

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{current_user.id}.{ext}"
    filepath = os.path.join(AVATAR_UPLOAD_DIR, filename)

    try:
        img = Image.open(file)
        # Crop to square centre
        w, h   = img.size
        side   = min(w, h)
        left   = (w - side) // 2
        top    = (h - side) // 2
        img    = img.crop((left, top, left + side, top + side))
        img    = img.resize((256, 256), Image.LANCZOS)
        img.save(filepath)
    except Exception:
        flash("Could not process image. Please try a different file.", "error")
        return redirect(url_for("profile"))

    current_user.avatar_url = filename
    db.session.commit()
    flash("Avatar updated.", "success")
    return redirect(url_for("profile"))


@app.route("/link-rl", methods=["POST"])
@login_required
def link_rl():
    rl_username = request.form.get("rl_username", "").strip()
    current_user.rl_username = rl_username
    db.session.commit()
    flash("Rocket League username saved.", "success")
    return redirect(url_for("profile"))


@app.route("/dashboard")
@login_required
def dashboard():
    player = request.args.get("player", "").strip()
    replays = []
    if player:
        try:
            data = search_replays_by_player(player, count=50)
            raw  = data.get("list", [])
            for r in raw:
                blue_names   = [p["name"].lower() for p in r.get("blue",   {}).get("players", [])]
                orange_names = [p["name"].lower() for p in r.get("orange", {}).get("players", [])]
                blue_goals   = r.get("blue",   {}).get("goals", 0) or 0
                orange_goals = r.get("orange", {}).get("goals", 0) or 0
                if any(player.lower() in name for name in blue_names):
                    r["result"] = "win" if blue_goals > orange_goals else "loss"
                elif any(player.lower() in name for name in orange_names):
                    r["result"] = "win" if orange_goals > blue_goals else "loss"
                else:
                    r["result"] = "unknown"
                replays.append(r)
        except Exception:
            replays = []
    return render_template("dashboard.html", player=player, replays=replays, user=current_user)


# ── Analytics route ────────────────────────────────────────────────────
def _compute_analytics(replays, player_lower):
    """Compute all analytics stats from a list of replay dicts."""
    wins = losses = 0
    map_wins = defaultdict(int)
    map_total = defaultdict(int)
    playlist_count = defaultdict(int)
    hour_count = [0] * 24
    diff_values, diff_labels = [], []
    goal_diffs = []
    goals_scored_list, goals_conceded_list = [], []

    for i, r in enumerate(replays):
        result = r.get("result", "unknown")
        if result == "win":   wins   += 1
        elif result == "loss": losses += 1

        map_name = r.get("map_name") or r.get("map_code") or "Unknown"
        map_total[map_name] += 1
        if result == "win": map_wins[map_name] += 1

        pl = r.get("playlist_id") or r.get("playlist_name") or "Unknown"
        playlist_count[pl] += 1

        # Hour of day from ISO date
        date_str = r.get("date", "")
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            hour_count[dt.hour] += 1
        except Exception:
            pass

        # Goal differential
        blue_goals   = r.get("blue",   {}).get("goals", 0) or 0
        orange_goals = r.get("orange", {}).get("goals", 0) or 0
        blue_names   = [p["name"].lower() for p in r.get("blue",   {}).get("players", [])]
        orange_names = [p["name"].lower() for p in r.get("orange", {}).get("players", [])]
        if any(player_lower in n for n in blue_names):
            diff = blue_goals - orange_goals
        elif any(player_lower in n for n in orange_names):
            diff = orange_goals - blue_goals
        else:
            diff = 0
        goal_diffs.append(diff)
        diff_labels.append(f"#{i+1}")
        diff_values.append(diff)

        # Goals scored / conceded for avg chart
        if any(player_lower in n for n in blue_names):
            goals_scored_list.append(blue_goals)
            goals_conceded_list.append(orange_goals)
        elif any(player_lower in n for n in orange_names):
            goals_scored_list.append(orange_goals)
            goals_conceded_list.append(blue_goals)

    total = len(replays)
    known = wins + losses
    wr    = round((wins / known * 100), 1) if known > 0 else 0.0

    # Best map by WR (min 2 games)
    map_wr = {m: round(map_wins[m] / map_total[m] * 100, 1) for m in map_total if map_total[m] >= 2}
    best_map    = max(map_wr, key=map_wr.get) if map_wr else "N/A"
    best_map_wr = map_wr.get(best_map, 0)

    # Top 6 maps by games played
    top_maps = sorted(map_total.keys(), key=lambda m: map_total[m], reverse=True)[:6]
    map_labels  = [m[:20] for m in top_maps]
    map_wr_vals = [round(map_wins[m] / map_total[m] * 100, 1) for m in top_maps]

    # Playlist
    top_pl    = max(playlist_count, key=playlist_count.get) if playlist_count else "N/A"
    top_pl_pct = round(playlist_count[top_pl] / total * 100) if total else 0
    pl_labels  = list(playlist_count.keys())[:6]
    pl_values  = [playlist_count[k] for k in pl_labels]

    # Streaks
    results = [r.get("result", "unknown") for r in replays]
    best_win, worst_loss, cur_win, cur_loss = 0, 0, 0, 0
    tmp_w, tmp_l = 0, 0
    for res in results:
        if res == "win":   tmp_w += 1; tmp_l = 0
        elif res == "loss": tmp_l += 1; tmp_w = 0
        best_win   = max(best_win, tmp_w)
        worst_loss = max(worst_loss, tmp_l)
    # Current streak (from tail)
    cur_streak = 0
    cur_type   = "—"
    if results:
        last = results[0]
        cur_type = last if last in ("win", "loss") else "—"
        for res in results:
            if res == last and last in ("win", "loss"): cur_streak += 1
            else: break

    # Avg duration
    avg_dur_s = int(sum(r.get("duration", 0) for r in replays) / total) if total > 0 else 0

    # Win rate trend (rolling 5)
    wr_trend_labels, wr_trend_values = [], []
    for i in range(4, len(results)):
        window = results[i-4:i+1]
        w = window.count("win")
        wr_trend_labels.append(f"#{i+1}")
        wr_trend_values.append(round(w / 5 * 100, 1))

    # Hour labels
    hour_labels = [f"{h:02d}:00" for h in range(24)]

    avg_diff = round(sum(goal_diffs) / len(goal_diffs), 1) if goal_diffs else 0
    avg_scored   = round(sum(goals_scored_list)   / len(goals_scored_list),   1) if goals_scored_list   else 0
    avg_conceded = round(sum(goals_conceded_list) / len(goals_conceded_list), 1) if goals_conceded_list else 0

    # Cumulative wins over time
    cumulative_wins = []
    running = 0
    for res in results:
        if res == "win": running += 1
        cumulative_wins.append(running)
    cum_labels = [f"#{i+1}" for i in range(len(results))]

    return {
        "total": total, "wins": wins, "losses": losses, "wr": wr,
        "best_map": best_map, "best_map_wr": best_map_wr,
        "top_playlist": top_pl, "top_playlist_pct": top_pl_pct,
        "best_win_streak": best_win, "worst_loss_streak": worst_loss,
        "current_streak": cur_streak, "current_streak_type": cur_type,
        "avg_dur_m": avg_dur_s // 60, "avg_dur_s": avg_dur_s % 60,
        "wr_trend_labels": wr_trend_labels, "wr_trend_values": wr_trend_values,
        "map_labels": map_labels, "map_wr_vals": map_wr_vals,
        "playlist_labels": pl_labels, "playlist_values": pl_values,
        "hour_labels": hour_labels, "hour_values": hour_count,
        "diff_labels": diff_labels, "diff_values": diff_values,
        "avg_diff": avg_diff,
        "avg_scored": avg_scored, "avg_conceded": avg_conceded,
        "cum_labels": cum_labels, "cumulative_wins": cumulative_wins,
    }


@app.route("/analytics")
@login_required
def analytics():
    player = request.args.get("player", "").strip()
    replays, stats = [], None

    if player:
        try:
            data = search_replays_by_player(player, count=50)
            raw  = data.get("list", [])
            for r in raw:
                blue_names   = [p["name"].lower() for p in r.get("blue",   {}).get("players", [])]
                orange_names = [p["name"].lower() for p in r.get("orange", {}).get("players", [])]
                blue_goals   = r.get("blue",   {}).get("goals", 0) or 0
                orange_goals = r.get("orange", {}).get("goals", 0) or 0
                if any(player.lower() in name for name in blue_names):
                    r["result"] = "win" if blue_goals > orange_goals else "loss"
                elif any(player.lower() in name for name in orange_names):
                    r["result"] = "win" if orange_goals > blue_goals else "loss"
                else:
                    r["result"] = "unknown"
                replays.append(r)
            if replays:
                stats = _compute_analytics(replays, player.lower())
        except Exception:
            replays = []

    return render_template("analytics.html", player=player, replays=replays, stats=stats, user=current_user)


@app.route("/hitbox", methods=["GET", "POST"])
@login_required
def hitbox_lookup():
    result   = None
    car_name = None
    all_cars = CarHitbox.query.order_by(CarHitbox.hitbox_class, CarHitbox.car_name).all()

    if request.method == "POST":
        car_name = request.form.get("car_name", "").strip()
        car = CarHitbox.query.filter(
            CarHitbox.car_name.ilike(f"%{car_name}%")
        ).first()
        result = {"car": car.car_name, "hitbox": car.hitbox_class, "found": True} if car \
            else {"car": car_name, "hitbox": None, "found": False}

    grouped = defaultdict(list)
    for car in all_cars:
        grouped[car.hitbox_class].append(car.car_name)

    return render_template("hitbox.html", result=result, car_name=car_name, grouped=grouped)


if __name__ == "__main__":
    import werkzeug.serving
    werkzeug.serving.WSGIRequestHandler.server_version = ""
    app.run(debug=True)