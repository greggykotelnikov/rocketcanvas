from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import re
import secrets
from sqlalchemy import func
from flask import current_app
from models import db, User, TwoFactorCode

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

MAX_2FA_ATTEMPTS = 5
EMAIL_RE    = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
USERNAME_RE = re.compile(r"[A-Za-z0-9_.\-]{3,30}")

def send_2fa_email(mail, user):
    code = str(secrets.randbelow(900000) + 100000)
    expires = datetime.utcnow() + timedelta(minutes=10)

    # Invalidate old codes
    TwoFactorCode.query.filter_by(user_id=user.id, used=False).update({"used": True})
    db.session.add(TwoFactorCode(user_id=user.id, code=code, expires_at=expires))
    db.session.commit()

    msg = Message("RocketCanvas | Your 2FA Code", recipients=[user.email])
    msg.body = f"Your verification code is: {code}\n\nExpires in 10 minutes."
    msg.html = f"""
    <div style="background:#0d0f14;padding:2rem;font-family:sans-serif;color:#e2e8f0;max-width:400px;margin:auto;border:1px solid #1f2433;">
        <h2 style="color:#00d4ff;margin-bottom:1rem;letter-spacing:0.1em;">ROCKETCANVAS</h2>
        <p style="color:#5a6380;margin-bottom:1.5rem;">Your verification code:</p>
        <div style="font-size:2.5rem;font-weight:bold;letter-spacing:0.3em;color:#fff;background:#13161e;padding:1rem;text-align:center;border:1px solid #1f2433;">
            {code}
        </div>
        <p style="color:#5a6380;margin-top:1rem;font-size:0.8rem;">Expires in 10 minutes. Do not share this code.</p>
    </div>
    """
    mail.send(msg)
    return code

_DUMMY_HASH = None

def _dummy_hash():
    """A real bcrypt hash (same cost factor) to compare against for unknown users."""
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        _DUMMY_HASH = bcrypt.generate_password_hash(secrets.token_hex(16)).decode("utf-8")
    return _DUMMY_HASH

def _try_send_2fa(mail, user):
    """Send a 2FA code, flashing an error instead of crashing if SMTP fails."""
    try:
        send_2fa_email(mail, user)
        return True
    except Exception:
        current_app.logger.exception("Failed to send 2FA email to user %s", user.id)
        session.pop("pending_user_id", None)
        flash("We couldn't send your verification code. Please try again later.", "error")
        return False

def register_auth_routes(app, mail, limiter):
    @app.route("/register", methods=["GET", "POST"])
    @limiter.limit("5 per minute; 20 per hour", methods=["POST"])
    def register():
        if request.method == "POST":
            email    = request.form.get("email", "").strip().lower()
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not EMAIL_RE.fullmatch(email) or len(email) > 120:
                flash("Please enter a valid email address.", "error")
                return render_template("login.html", mode="register")

            if not USERNAME_RE.fullmatch(username):
                flash("Username must be 3-30 characters: letters, numbers, '_', '-' or '.'.", "error")
                return render_template("login.html", mode="register")
            
            # bcrypt only looks at the first 72 bytes; anything longer would
            # silently be ignored, so reject it instead.
            if len(password.encode("utf-8")) > 72:
                flash("Password is too long (max 72 bytes).", "error")
                return render_template("login.html", mode="register")
            
            if len(password) < 8:
                flash("Password must be at least 8 characters long.", "error")
                return render_template("login.html", mode="register")
            
            if not any(char.isdigit() for char in password):
                flash("Password must contain at least one number.", "error")
                return render_template("login.html", mode="register")
            
            if not any(not char.isalnum() for char in password):
                flash("Password must contain at least one special character.", "error")
                return render_template("login.html", mode="register")

            if User.query.filter_by(email=email).first():
                flash("Email already registered.", "error")
                return render_template("login.html", mode="register")
            # Case-insensitive so "Pilot" can't impersonate "pilot".
            if User.query.filter(func.lower(User.username) == username.lower()).first():
                flash("Username taken.", "error")
                return render_template("login.html", mode="register")

            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(email=email, username=username, password_hash=hashed)
            db.session.add(user)
            db.session.commit()

            session["pending_user_id"] = user.id
            if not _try_send_2fa(mail, user):
                return render_template("login.html", mode="login")
            return redirect(url_for("verify"))

        return render_template("login.html", mode="register")

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute; 30 per hour", methods=["POST"])
    def login():
        if request.method == "POST":
            email    = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(email=email).first()

            # Always run a bcrypt check, even for unknown emails, so response
            # time doesn't reveal which addresses have accounts.
            password_hash = user.password_hash if user else _dummy_hash()
            password_ok = bcrypt.check_password_hash(password_hash, password)
            if not user or not password_ok:
                flash("Invalid email or password.", "error")
                return render_template("login.html", mode="login")

            session["pending_user_id"] = user.id
            if not _try_send_2fa(mail, user):
                return render_template("login.html", mode="login")
            return redirect(url_for("verify"))

        return render_template("login.html", mode="login")

    @app.route("/verify", methods=["GET", "POST"])
    @limiter.limit("10 per minute", methods=["POST"])
    def verify():
        user_id = session.get("pending_user_id")
        if not user_id:
            return redirect(url_for("login"))

        if request.method == "POST":
            entered = request.form.get("code", "").strip()
            now = datetime.utcnow()

            # Only the most recently issued code is live (older ones are
            # invalidated in send_2fa_email), so check against that one and
            # count failures on it.
            record = TwoFactorCode.query.filter_by(
                user_id=user_id, used=False
            ).order_by(TwoFactorCode.id.desc()).first()

            if not record or record.expires_at < now:
                session.pop("pending_user_id", None)
                flash("Your code has expired. Please log in again.", "error")
                return redirect(url_for("login"))

            if not secrets.compare_digest(record.code, entered):
                record.attempts += 1
                if record.attempts >= MAX_2FA_ATTEMPTS:
                    record.used = True
                    db.session.commit()
                    session.pop("pending_user_id", None)
                    flash("Too many incorrect codes. Please log in again.", "error")
                    return redirect(url_for("login"))
                db.session.commit()
                flash("Invalid or expired code.", "error")
                return render_template("verify.html")

            record.used = True
            db.session.commit()

            user = db.session.get(User, user_id)
            if user is None:
                session.pop("pending_user_id", None)
                return redirect(url_for("login"))
            login_user(user)
            session.pop("pending_user_id", None)
            return redirect(url_for("profile"))

        return render_template("verify.html")

    @app.route("/verify/resend", methods=["POST"])
    @limiter.limit("3 per 10 minutes")
    def resend_code():
        """Issue a fresh 2FA code for the login in progress.

        send_2fa_email() invalidates the previous code, so a resend also
        resets the attempt counter without letting an attacker accumulate
        guesses across several live codes.
        """
        user_id = session.get("pending_user_id")
        user = db.session.get(User, user_id) if user_id else None
        if user is None:
            return redirect(url_for("login"))
        if _try_send_2fa(mail, user):
            flash("A new code has been sent to your email.", "success")
            return redirect(url_for("verify"))
        return redirect(url_for("login"))

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        # POST-only (CSRF-protected) so other sites can't log users out
        # with a simple <img src="/logout">.
        logout_user()
        return redirect(url_for("login"))