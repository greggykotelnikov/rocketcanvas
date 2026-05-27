# 🚀 RocketCanvas

> A Rocket League stat tracker, hitbox lookup tool, and player analytics dashboard which is powered by [ballchasing.com](https://ballchasing.com).

---

## Features

| Feature | Description |
|---|---|
| 🔐 **Auth + 2FA** | Email-verified login with two-factor authentication |
| 📊 **Dashboard** | Search any player, see replays, win rate trend & goals chart |
| 📈 **Analytics** | Deep-dive: map win rates, hourly activity, playlist breakdown, streaks, goal differential |
| 🚗 **Hitbox Lookup** | Find which hitbox class every Rocket League car uses |
| 👤 **Profile** | Avatar upload, RL rank title, bio, RL username linking |
| 🌙 **Dark / Light Mode** | Toggle persisted in localStorage |

---

## Local Setup

### 1. Clone & create venv

```bash
git clone https://github.com/yourname/rocketcanvas.git
cd rocketcanvas
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
SECRET_KEY=your-random-secret-key
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your@gmail.com
BALLCHASING_TOKEN=your-ballchasing-api-token
```

> Get a ballchasing API token at [ballchasing.com/upload](https://ballchasing.com/upload)

### 4. Seed the hitbox database

```bash
python seed_hitboxes.py #upd: does not work since my ML model from teachable machine did not prove to be a successful solution due to the lack of angles and cases for each of the car hitboxes.
```

### 5. Run

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask |
| Database | SQLite via Flask-SQLAlchemy |
| Auth | Flask-Login + Flask-Bcrypt + 2FA email codes |
| Security | Flask-WTF (CSRF), Flask-Limiter, security headers |
| Mail | Flask-Mail (Gmail SMTP) |
| Charts | Chart.js |
| Fonts | Google Fonts — Rajdhani + Share Tech Mono |
| Images | Pillow (avatar processing) |

---

## Project Structure

```
rocketcanvas/
├── app.py              # Main Flask application, all routes
├── auth.py             # Login / register / 2FA route registration
├── models.py           # SQLAlchemy models (User, CarHitbox, TwoFactorCode)
├── ballchasing.py      # ballchasing.com API client
├── seed_hitboxes.py    # One-time DB seeder for car hitbox data
├── ml/
│   ├── keras_model.h5  # Trained Keras model for hitbox image prediction
│   └── labels.txt      # Class labels
├── static/
│   ├── images/         # Logo + login page images
│   └── uploads/
│       └── avatars/    # User avatar photos
├── templates/
│   ├── base.html       # Shared layout, nav, dark mode, CSS tokens
│   ├── login.html      # Login + register page
│   ├── verify.html     # 2FA code entry
│   ├── profile.html    # User profile + settings
│   ├── dashboard.html  # Player search + replay list
│   ├── analytics.html  # Performance analytics charts
│   └── hitbox.html     # Hitbox lookup tool
└── requirements.txt
```

---

## Security

- All POST forms use **CSRF tokens** (Flask-WTF)  
- Login is **rate-limited** (Flask-Limiter)  
- Passwords hashed with **bcrypt**  
- 2FA codes generated with **`secrets`** (cryptographically secure)  
- HTTP security headers: `X-Frame-Options`, `CSP`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`  
- `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SAMESITE` set  

---

## License

MIT
