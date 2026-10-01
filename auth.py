from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import secrets
from flask import current_app
from models import db, User, TwoFactorCode

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

MAX_2FA_ATTEMPTS = 5

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

            if len(username) > 80:
                flash("Username must be under 80 characters.", "error")
                return render_template("login.html", mode="register")
            
            if len(password) > 100:
                flash("Password is too long.", "error")
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
            if User.query.filter_by(username=username).first():
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

            if not user or not bcrypt.check_password_hash(user.password_hash, password):
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

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))