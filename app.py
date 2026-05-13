import os
from flask import Flask, flash, request, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from models import db, User
from auth import register_auth_routes, bcrypt as auth_bcrypt
from ballchasing import search_replays_by_player
from models import CarHitbox
from collections import defaultdict

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"]                = os.getenv("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"]   = "sqlite:///rocketcanvas.db"
app.config["MAIL_SERVER"]               = "smtp.gmail.com"
app.config["MAIL_PORT"]                 = 587
app.config["MAIL_USE_TLS"]              = True
app.config["MAIL_USERNAME"]             = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"]             = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"]       = os.getenv("MAIL_DEFAULT_SENDER")
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_HTTPONLY'] = True

db.init_app(app)
auth_bcrypt.init_app(app)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

register_auth_routes(app, mail)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/dashboard")
@login_required
def dashboard():
    player = request.args.get("player", "").strip()
    replays = []
    if player:
        try:
            data = search_replays_by_player(player, count=50)
            raw  = data.get("list", [])

            if raw:
                import json                         #temp
                print(json.dumps(raw[0], indent=2))

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
        except Exception as e:
            replays = []
    return render_template("dashboard.html", player=player, replays=replays, user=current_user)

    

@app.route("/link-rl", methods=["POST"])
@login_required
def link_rl():
    from flask import redirect, url_for
    rl_username = request.form.get("rl_username", "").strip()
    current_user.rl_username = rl_username
    db.session.commit()
    flash("Rocket League username saved.", "success")
    return redirect(url_for("profile"))


@app.route('/hitbox', methods=['GET', 'POST'])
@login_required
def hitbox_lookup():
    result = None
    car_name = None
    all_cars = CarHitbox.query.order_by(CarHitbox.hitbox_class, CarHitbox.car_name).all()
 
    if request.method == 'POST':
        car_name = request.form.get('car_name', '').strip()
        car = CarHitbox.query.filter(
            CarHitbox.car_name.ilike(f'%{car_name}%')
        ).first()
        if car:
            result = {'car': car.car_name, 'hitbox': car.hitbox_class, 'found': True}
        else:
            result = {'car': car_name, 'hitbox': None, 'found': False}
 
    # Group cars by hitbox class for the full table 
    grouped = defaultdict(list)
    for car in all_cars:
        grouped[car.hitbox_class].append(car.car_name)
 
    return render_template('hitbox.html', result=result, car_name=car_name, grouped=grouped)
 


if __name__ == "__main__":
    app.run(debug=True)