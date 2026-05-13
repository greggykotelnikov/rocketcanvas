from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rl_username   = db.Column(db.String(80), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class TwoFactorCode(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code       = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False)


class CarHitbox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_name = db.Column(db.String(100), nullable=False, unique=True)
    hitbox_class = db.Column(db.String(50), nullable=False)