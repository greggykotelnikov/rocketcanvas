import os
import secrets as _secrets
import uuid
from collections import defaultdict
from datetime import datetime
from functools import lru_cache

from flask import Flask, flash, request, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import werkzeug.serving
from PIL import Image

# ── Suppress server version leakage (ZAP: Server Leaks Version Info) ──
werkzeug.serving.WSGIRequestHandler.server_version = ""
werkzeug.serving.WSGIRequestHandler.sys_version = ""

from models import db, User
from auth import register_auth_routes, bcrypt as auth_bcrypt
import requests
from ballchasing import search_replays_by_player, BallchasingConfigError
from models import CarHitbox, CarDesign
from sqlalchemy import func

load_dotenv()

# ── App factory ────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"]                  = os.getenv("SECRET_KEY") or _secrets.token_hex(32)
app.config["SQLALCHEMY_DATABASE_URI"]     = os.getenv("DATABASE_URL", "sqlite:///rocketcanvas.db")
app.config["MAIL_SERVER"]                 = "smtp.gmail.com"
app.config["MAIL_PORT"]                   = 587
app.config["MAIL_USE_TLS"]                = True
app.config["MAIL_USERNAME"]               = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"]               = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"]         = os.getenv("MAIL_DEFAULT_SENDER")
app.config["SESSION_COOKIE_SAMESITE"]     = "Lax"
app.config["SESSION_COOKIE_SECURE"]       = True
app.config["SESSION_COOKIE_HTTPONLY"]     = True
app.config["WTF_CSRF_ENABLED"]            = True
app.config["MAX_CONTENT_LENGTH"]          = 4 * 1024 * 1024   # 4 MB avatar limit

if not os.getenv("SECRET_KEY"):
    app.logger.warning(
        "SECRET_KEY is not set; using a random key. All sessions will be "
        "invalidated whenever the server restarts. Set SECRET_KEY in .env."
    )

AVATAR_UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads", "avatars")
DESIGN_UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads", "designs")
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}
CARD_TEMPLATES    = {"legendary", "golden", "chroma", "carbon", "holographic"}
PLATFORMS = ["Steam", "Epic Games", "PlayStation", "Xbox", "Nintendo"]
RANKS = [
    f"{tier} {div}"
    for tier in ("Bronze", "Silver", "Gold", "Platinum", "Diamond", "Champion", "Grand Champion")
    for div in ("I", "II", "III")
] + ["Supersonic Legend"]

os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)
os.makedirs(DESIGN_UPLOAD_DIR, exist_ok=True)

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

@limiter.request_filter
def _exempt_static_assets():
    # Pages pull in dozens of CSS/JS/sprite files; counting those against the
    # global limit locks users out after a couple of page loads.
    return request.endpoint in ("static", "manifest", "service_worker")

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

register_auth_routes(app, mail, limiter)

# ── DB init + column migration shim ────────────────────────────────────
with app.app_context():
    db.create_all()
    # Add new columns if upgrading from older schema
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError
    with db.engine.connect() as conn:
        for col, defn in [("rank", "VARCHAR(50)"), ("bio", "VARCHAR(300)"), ("avatar_url", "VARCHAR(200)"), ("platform", "VARCHAR(50)")]:
            try:
                conn.execute(text(f"ALTER TABLE user ADD COLUMN {col} {defn}"))
                conn.commit()
            except OperationalError:
                pass  # Column already exists
        # CarDesign new columns
        for col, defn in [("card_template", "VARCHAR(50) DEFAULT 'legendary'"), ("overlay_title", "VARCHAR(100)")]:
            try:
                conn.execute(text(f"ALTER TABLE car_design ADD COLUMN {col} {defn}"))
                conn.commit()
            except OperationalError:
                pass  # Column already exists
        # TwoFactorCode new columns
        try:
            conn.execute(text("ALTER TABLE two_factor_code ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0"))
            conn.commit()
        except OperationalError:
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

class SecurityHeadersMiddleware:
    def __init__(self, app_wsgi):
        self.app_wsgi = app_wsgi

    def __call__(self, environ, start_response):
        # Generate a nonce per request if we wanted to inject it into CSP,
        # but CSP relies on the Flask context which isn't easily available here.
        # So we'll let Flask handle CSP and we handle HSTS and others here.
        def custom_start_response(status, headers, exc_info=None):
            header_keys = [h[0].lower() for h in headers]
            
            if 'strict-transport-security' not in header_keys:
                headers.append(('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload'))
            if 'x-frame-options' not in header_keys:
                headers.append(('X-Frame-Options', 'DENY'))
            if 'x-content-type-options' not in header_keys:
                headers.append(('X-Content-Type-Options', 'nosniff'))
            if 'x-xss-protection' not in header_keys:
                # '0' per OWASP: the legacy XSS auditor is removed from modern
                # browsers and in older ones '1; mode=block' could be abused to
                # leak data. The nonce-based CSP is the real XSS defence.
                headers.append(('X-XSS-Protection', '0'))
            if 'referrer-policy' not in header_keys:
                headers.append(('Referrer-Policy', 'strict-origin-when-cross-origin'))
            if 'permissions-policy' not in header_keys:
                headers.append(('Permissions-Policy', 'geolocation=(), microphone=(), camera=()'))
            
            # Remove Server header
            headers = [h for h in headers if h[0].lower() != 'server']
            
            return start_response(status, headers, exc_info)

        return self.app_wsgi(environ, custom_start_response)

app.wsgi_app = SecurityHeadersMiddleware(app.wsgi_app)

@app.after_request
def add_csp_header(response):
    from flask import g
    nonce = getattr(g, 'nonce', '')
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
        f"style-src 'self' 'nonce-{nonce}' fonts.googleapis.com https://unpkg.com; "
        "font-src 'self' fonts.gstatic.com; "
        "img-src 'self' data: https://unpkg.com https://*.tile.openstreetmap.org; "
        "connect-src 'self'; "
        "worker-src 'self'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )
    return response

# ── Helper ─────────────────────────────────────────────────────────────
def allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXT
MAX_IMAGE_PIXELS = 25_000_000   # ~5000x5000; reject decompression bombs


def _open_uploaded_image(file):
    """Open an uploaded image safely, raising ValueError if it's unusable.

    verify() rejects truncated / non-image payloads, and the pixel cap is
    checked from the header *before* decoding, so a small file claiming
    huge dimensions can't exhaust memory.
    """
    img = Image.open(file)
    img.verify()
    file.seek(0)
    img = Image.open(file)
    w, h = img.size
    if w * h > MAX_IMAGE_PIXELS:
        raise ValueError(f"image too large: {w}x{h}")
    return img


def _delete_old_avatar(filename):
    """Remove a previously uploaded avatar file, ignoring missing files."""
    if not filename:
        return
    path = os.path.join(AVATAR_UPLOAD_DIR, os.path.basename(filename))
    try:
        os.remove(path)
    except OSError:
        pass


# ── PWA Routes ─────────────────────────────────────────────────────
@app.route("/manifest.json")
def manifest():
    return send_from_directory(app.static_folder, "manifest.json",
                               mimetype="application/manifest+json")

@app.route("/sw.js")
def service_worker():
    response = send_from_directory(app.static_folder, "sw.js",
                                    mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response

@app.route("/offline")
def offline():
    return render_template("offline.html")


# ── Routes ─────────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user, platforms=PLATFORMS, ranks=RANKS)


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    rank     = request.form.get("rank", "").strip()
    platform = request.form.get("platform", "").strip()
    # Rank and platform come from fixed dropdowns; ignore anything else so
    # arbitrary strings can't be stored and shown on the profile.
    current_user.rl_username = request.form.get("rl_username", "").strip()[:80] or None
    current_user.rank        = rank if rank in RANKS else None
    current_user.bio         = request.form.get("bio", "").strip()[:300] or None
    current_user.platform    = platform if platform in PLATFORMS else None
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

    # Always re-encode as PNG under a fresh name: the service worker caches
    # /static/ cache-first, so reusing "<id>.<ext>" meant a new avatar never
    # showed up, and saving RGBA/palette images as .jpg raised an error.
    filename = f"{current_user.id}_{uuid.uuid4().hex[:12]}.png"
    filepath = os.path.join(AVATAR_UPLOAD_DIR, filename)

    try:
        img = _open_uploaded_image(file)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        # Crop to square centre
        w, h   = img.size
        side   = min(w, h)
        left   = (w - side) // 2
        top    = (h - side) // 2
        img    = img.crop((left, top, left + side, top + side))
        img    = img.resize((256, 256), Image.LANCZOS)
        img.save(filepath, format="PNG")
    except Exception:
        flash("Could not process image. Please try a different file.", "error")
        return redirect(url_for("profile"))

    _delete_old_avatar(current_user.avatar_url)
    current_user.avatar_url = filename
    db.session.commit()
    flash("Avatar updated.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/avatar/preset", methods=["POST"])
@login_required
def set_preset_avatar():
    import shutil
    preset = request.form.get("preset")
    valid_presets = ["octane.png", "dominus.png", "fennec.png"]
    if preset in valid_presets:
        src = os.path.join(app.root_path, "static", "avatars", "placeholders", preset)
        filename = f"{current_user.id}_{preset}"
        dst = os.path.join(AVATAR_UPLOAD_DIR, filename)
        shutil.copyfile(src, dst)
        if current_user.avatar_url != filename:
            _delete_old_avatar(current_user.avatar_url)
        current_user.avatar_url = filename
        db.session.commit()
        flash("Avatar updated.", "success")
    else:
        flash("Invalid preset selected.", "error")
    return redirect(url_for("profile"))


@app.route("/gallery")
@login_required
def gallery():
    designs = CarDesign.query.order_by(CarDesign.created_at.desc()).all()
    return render_template("gallery.html", designs=designs)

@app.route("/garage")
@login_required
def garage():
    base_dir = os.path.join(app.root_path, "static", "images", "car-constructor")
    
    def get_files(subdir):
        path = os.path.join(base_dir, subdir)
        if not os.path.exists(path):
            return []
        return sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
    
    def get_nested_files(subdir):
        path = os.path.join(base_dir, subdir)
        if not os.path.exists(path):
            return {}
        result = {}
        for d in os.listdir(path):
            d_path = os.path.join(path, d)
            if os.path.isdir(d_path):
                result[d] = sorted([f for f in os.listdir(d_path) if os.path.isfile(os.path.join(d_path, f))])
        return result

    bodies = get_files("1 Bodies")
    chassis = get_nested_files("2 Chassis")
    additions = get_files("3 Additions")
    patches = get_files("4 Patches")
    effects = get_files("5 Effects")

    return render_template(
        "garage.html",
        bodies=bodies,
        chassis=chassis,
        additions=additions,
        patches=patches,
        effects=effects
    )


@app.route("/gallery/upload", methods=["POST"])
@login_required
def upload_design():
    # Enforce the same limits as the form/DB columns: maxlength in the HTML
    # is trivially bypassed and SQLite does not enforce VARCHAR lengths.
    title = request.form.get("title", "").strip()[:150]
    file = request.files.get("design_image")
    card_template = request.form.get("card_template", "legendary")
    overlay_title = request.form.get("overlay_title", "").strip()[:100] or None
    if card_template not in CARD_TEMPLATES:
        # Rendered into a CSS class on the gallery card; only allow known styles.
        card_template = "legendary"
    if not title:
        flash("Title is required.", "error")
        return redirect(url_for("gallery"))
    if not file or file.filename == "":
        flash("No image selected.", "error")
        return redirect(url_for("gallery"))
    if not allowed_image(file.filename):
        flash("Only image files are allowed.", "error")
        return redirect(url_for("gallery"))
        
    # Re-encode as PNG: converting to RGB and then saving under the user's
    # ".gif"/".webp" extension produced a mismatched or lossy file.
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(DESIGN_UPLOAD_DIR, filename)
    
    try:
        img = _open_uploaded_image(file)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail((1920, 1080), Image.LANCZOS)
        img.save(filepath, format="PNG")
    except Exception:
        flash("Could not process image.", "error")
        return redirect(url_for("gallery"))
        
    new_design = CarDesign(user_id=current_user.id, title=title, image_filename=filename, card_template=card_template, overlay_title=overlay_title)
    db.session.add(new_design)
    db.session.commit()
    flash("Design uploaded successfully!", "success")
    
    return redirect(url_for("gallery"))


@app.route("/link-rl", methods=["POST"])
@login_required
def link_rl():
    rl_username = request.form.get("rl_username", "").strip()[:80]
    current_user.rl_username = rl_username or None
    db.session.commit()
    flash("Rocket League username saved.", "success")
    return redirect(url_for("profile"))


@app.route("/dashboard")
@login_required
def dashboard():
    player = request.args.get("player", "").strip()[:64]
    replays = _fetch_player_replays(player) if player else []
    return render_template("dashboard.html", player=player, replays=replays, user=current_user)


# ── Ballchasing helpers ────────────────────────────────────────────────
def _player_team(replay, player_lower):
    """Return "blue"/"orange" for the team the searched player was on, or None.

    Prefer an exact (case-insensitive) name match; fall back to a substring
    match. Substring-only meant a search for "max" was attributed to
    whichever team had "Maxwell" in it first.
    """
    names = {
        team: [(p.get("name") or "").lower() for p in replay.get(team, {}).get("players", [])]
        for team in ("blue", "orange")
    }
    for team in ("blue", "orange"):
        if player_lower in names[team]:
            return team
    for team in ("blue", "orange"):
        if any(player_lower in n for n in names[team]):
            return team
    return None


def _team_goals(replay):
    blue   = replay.get("blue",   {}).get("goals", 0) or 0
    orange = replay.get("orange", {}).get("goals", 0) or 0
    return blue, orange


def _fetch_player_replays(player):
    """Fetch the player's recent replays and tag each with team and result.

    Shared by /dashboard and /analytics (previously copy-pasted). API errors
    are surfaced as a flash message instead of silently showing no matches.
    """
    try:
        data = search_replays_by_player(player, count=50)
    except BallchasingConfigError:
        flash("Replay search isn't configured on this server (missing Ballchasing API key).", "error")
        return []
    except (requests.RequestException, ValueError):
        app.logger.exception("Ballchasing search failed for %r", player)
        flash("Couldn't reach ballchasing.com right now. Please try again later.", "error")
        return []

    player_lower = player.lower()
    replays = []
    for r in data.get("list", []):
        team = _player_team(r, player_lower)
        blue_goals, orange_goals = _team_goals(r)
        r["player_team"] = team
        if team == "blue":
            r["result"] = "win" if blue_goals > orange_goals else "loss"
        elif team == "orange":
            r["result"] = "win" if orange_goals > blue_goals else "loss"
        else:
            r["result"] = "unknown"
        replays.append(r)
    return replays


# ── Analytics route ────────────────────────────────────────────────────
def _compute_analytics(replays, player_lower):
    """Compute all analytics stats from a list of replay dicts."""
    wins = losses = 0
    map_wins = defaultdict(int)
    map_total = defaultdict(int)
    playlist_count = defaultdict(int)
    hour_count = [0] * 24
    diff_values, diff_labels = [], []
    goals_scored_list, goals_conceded_list = [], []

    # Ballchasing returns newest first. Time-series charts read left-to-right
    # as oldest-to-newest, so walk the matches chronologically. The current
    # streak still counts back from the most recent match below.
    chronological = list(reversed(replays))

    for i, r in enumerate(chronological):
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
        except (ValueError, TypeError, AttributeError):
            pass

        # Goal differential / goals scored & conceded, from the player's side
        blue_goals, orange_goals = _team_goals(r)
        team = r.get("player_team") or _player_team(r, player_lower)
        if team == "blue":
            scored, conceded = blue_goals, orange_goals
        elif team == "orange":
            scored, conceded = orange_goals, blue_goals
        else:
            scored = conceded = None
        diff = scored - conceded if scored is not None else 0
        diff_labels.append(f"#{i+1}")
        diff_values.append(diff)
        if scored is not None:
            goals_scored_list.append(scored)
            goals_conceded_list.append(conceded)

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
    # Six most-played playlists (was: first six encountered, unsorted)
    pl_labels  = sorted(playlist_count, key=playlist_count.get, reverse=True)[:6]
    pl_values  = [playlist_count[k] for k in pl_labels]

    # Streaks (oldest -> newest)
    results = [r.get("result", "unknown") for r in chronological]
    best_win, worst_loss = 0, 0
    tmp_w, tmp_l = 0, 0
    for res in results:
        if res == "win":   tmp_w += 1; tmp_l = 0
        elif res == "loss": tmp_l += 1; tmp_w = 0
        best_win   = max(best_win, tmp_w)
        worst_loss = max(worst_loss, tmp_l)
    # Current streak, counting back from the most recent match
    cur_streak = 0
    cur_type   = "n/a"
    if results:
        last = results[-1]
        cur_type = last if last in ("win", "loss") else "n/a"
        for res in reversed(results):
            if res == last and last in ("win", "loss"): cur_streak += 1
            else: break

    # Avg duration
    # Ballchasing can return null for duration; treat it as 0 instead of crashing
    avg_dur_s = int(sum(r.get("duration") or 0 for r in replays) / total) if total > 0 else 0

    # Win rate trend (rolling 5)
    wr_trend_labels, wr_trend_values = [], []
    for i in range(4, len(results)):
        window = results[i-4:i+1]
        w = window.count("win")
        wr_trend_labels.append(f"#{i+1}")
        wr_trend_values.append(round(w / 5 * 100, 1))

    # Hour labels
    hour_labels = [f"{h:02d}:00" for h in range(24)]

    # Averages only over games where we know which team the player was on;
    # unknown games were previously counted as a 0 goal differential.
    known_games  = len(goals_scored_list)
    avg_scored   = round(sum(goals_scored_list)   / known_games, 1) if known_games else 0
    avg_conceded = round(sum(goals_conceded_list) / known_games, 1) if known_games else 0
    avg_diff     = round((sum(goals_scored_list) - sum(goals_conceded_list)) / known_games, 1) if known_games else 0

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
    player = request.args.get("player", "").strip()[:64]
    replays = _fetch_player_replays(player) if player else []
    stats = _compute_analytics(replays, player.lower()) if replays else None

    return render_template("analytics.html", player=player, replays=replays, stats=stats, user=current_user)


@app.route("/hitbox", methods=["GET", "POST"])
@login_required
def hitbox_lookup():
    result   = None
    car_name = None
    all_cars = CarHitbox.query.order_by(CarHitbox.hitbox_class, CarHitbox.car_name).all()

    if request.method == "POST":
        car_name = request.form.get("car_name", "").strip()[:100]
        car = None
        if car_name:
            # Exact (case-insensitive) match first so "Octane" doesn't resolve
            # to "Octane ZSR"; then the shortest substring match, with LIKE
            # wildcards in the user's input escaped. An empty search used to
            # match "%%", i.e. every car, and report the first one as found.
            car = CarHitbox.query.filter(func.lower(CarHitbox.car_name) == car_name.lower()).first()
            if car is None:
                escaped = car_name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                car = CarHitbox.query.filter(
                    CarHitbox.car_name.ilike(f"%{escaped}%", escape="\\")
                ).order_by(func.length(CarHitbox.car_name)).first()
        result = {"car": car.car_name, "hitbox": car.hitbox_class, "found": True} if car \
            else {"car": car_name, "hitbox": None, "found": False}

    grouped = defaultdict(list)
    for car in all_cars:
        grouped[car.hitbox_class].append(car.car_name)

    return render_template(
        "hitbox.html",
        result=result,
        car_name=car_name,
        grouped=grouped
    )

@app.route("/heatmap")
@login_required
def heatmap():
    return render_template("heatmap.html")


@app.route("/parse-replay", methods=["POST"])
@login_required
def parse_replay():
    from flask import jsonify
    from replay_parser import parse_replay_positions
    import tempfile
    
    file = request.files.get("replay_file")
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No file uploaded."}), 400
        
    if not file.filename.lower().endswith(".replay"):
        return jsonify({"success": False, "error": "Invalid file type. Must be a .replay file."}), 400

    fd, temp_path = tempfile.mkstemp(suffix=".replay")
    os.close(fd)
    try:
        file.save(temp_path)
        player_heatmaps = parse_replay_positions(temp_path)
    except Exception:
        # Log the details server-side; don't echo exception text (paths,
        # internals) back to the client.
        app.logger.exception("Replay parsing failed")
        return jsonify({"success": False, "error": "Failed to parse replay file."}), 500
    finally:
        # Always remove the upload, even if parsing raised.
        try:
            os.remove(temp_path)
        except OSError:
            pass

    if not player_heatmaps:
        return jsonify({"success": False, "error": "Could not extract positions from replay."}), 400

    return jsonify({"success": True, "players": player_heatmaps})


@app.route("/recommend")
@login_required
def recommend():
    return render_template("recommend.html")




if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode, ssl_context=('localhost+2.pem', 'localhost+2-key.pem'))