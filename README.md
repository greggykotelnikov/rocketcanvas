# RocketCanvas

A premium, feature-rich web application for Rocket League players. RocketCanvas integrates match history tracking via the Ballchasing API, a custom 2D garage constructor, a 3D WebGL hitbox visualiser, positional heatmaps parsed from raw `.replay` files, and personalised page-by-page guided tours complete with procedural sound effect synthesis.

---

## Core Capabilities

* **Dashboard & Match Tracking**: Search any player to load their recent match history, win rates, and statistics directly from the Ballchasing.com API.
* **Match Analytics**: Multi-chart trends analyzing map-specific win rates, hourly playtime distribution, playlist breakdowns, current/longest streaks, and rolling win rate margins.
* **Holographic 3D Hitbox Visualiser**: Interactive 3D wireframe render of all six official Rocket League hitbox classes (Octane, Dominus, Breakout, Hybrid, Plank, Merc) with real-time yaw/pitch rotations, telemetry stats, and custom dimensions.
* **Positional Heatmaps**: Upload raw Rocket League `.replay` files to extract 2D spatial coordinate heatmaps of player movement on the pitch.
* **2D Garage Builder**: Layer-based sprite editor to customise vehicles with bodies, chassis paint, decals, additions, and special effects.
* **Preset Trading Card Gallery**: Upload and mint custom vehicle presets into stylized rarity-based trading cards (Legendary, Golden, Chroma Sparkle, Carbon Fiber, Holographic).
* **Persona-based Guided Tours**: Interactive, natural TTS-voiced walk-throughs on every page featuring custom procedural audio blip synthesis.
* **Progressive Web App (PWA)**: Desktop/mobile installable PWA with offline caching support via a registered service worker.

---

## Technology Stack

* **Backend**: Python 3.11 , Flask
* **Database**: SQLite via Flask-SQLAlchemy
* **Authentication**: Flask-Login + Flask-Bcrypt (with secure 2-Factor Authentication mail-verify codes)
* **Frontend**: Vanilla CSS, JavaScript, HTML5 Canvas
* **Libraries**: Chart.js (analytics rendering)
* **API Integration**: ballchasing.com REST API
* **Security & Utilities**: Flask-WTF (CSRF protection), Flask-Limiter (rate-limiting), Pillow (avatar crop/resize)

---

## Security Architecture

* **Cross-Site Request Forgery (CSRF)**: Enforced globally via WTForms and Flask-WTF CSRF tokens on all POST/PUT routes.
* **Content Security Policy (CSP)**: Secure HTTP response headers injecting cryptographically random script/style nonces (`g.nonce`) to block XSS.
* **Session Cookies**: Hardened cookie attributes (`HTTPOnly`, `Secure`, `SameSite=Lax`) to mitigate session hijacking.
* **Rate Limiting**: Custom route limits (e.g. login/register restrictions) powered by Flask-Limiter to defend against brute-force attacks.
* **Encryption**: Strict password hashing using Bcrypt salt rounds.

---

## File Structure

```
rocketcanvas/
├── app.py                  # Main Flask application and routing
├── auth.py                 # Authentication, register, and 2FA flow logic
├── models.py               # Database schemas (User, CarHitbox, CarDesign)
├── ballchasing.py          # API client for ballchasing.com query resolution
├── replay_parser.py        # Python parser extracting player positions from binary replays
├── seed_hitboxes.py        # Database seeder injecting official car dimensions
├── requirements.txt        # Python package dependencies
├── templates/              # HTML layout templates
│   ├── base.html           # Shared layout, nav-bar, theme controls, and footer
│   ├── login.html          # Authentication gate (sign-in & register)
│   ├── verify.html         # 2FA code verification panel
│   ├── profile.html        # Account management, platform link, and avatar selector
│   ├── dashboard.html      # Player search and match history feed
│   ├── gallery.html        # Trading card gallery and design uploader
│   ├── garage.html         # Layer-based 2D car preset editor
│   ├── analytics.html      # Chart-based performance trends
│   ├── heatmap.html        # Positional coordinate heatmap upload and display
│   ├── hitbox.html         # 3D interactive hitbox wireframe engine
│   ├── recommend.html      # Smart training recommendations based on match stats
│   └── offline.html        # Service Worker fallback page when network is unavailable
├── static/                 # Static asset containers
│   ├── css/                # Custom styling stylesheets (dialogue, cards, loader)
│   ├── js/                 # Client scripts (music player, canvas effects, guide, charts)
│   ├── sounds/             # Sound packs and background ambient loops
│   ├── images/             # Vector icons, backdrops, and builder layers
│   └── uploads/            # User-minted designs and custom avatar images
└── scratch/                # Developer helper scripts
```

---

## Installation and Local Setup

### Prerequisite: OpenSSL / HTTPS Setup
For secure cookies, Web Audio context, and PWA service workers, the application is configured to run over HTTPS. Local development uses a self-signed certificate (`localhost+2.pem` and `localhost+2-key.pem`). 

Ensure you have your localhost certs in the project root before starting the server. If generating new ones, you can use `mkcert`:
```bash
mkcert localhost 127.0.0.1 ::1
```

### 1. Set Up Virtual Environment
Clone the repository and initialize a Python virtual environment:
```bash
git clone https://github.com/greggykotelnikov/rocketcanvas.git
cd rocketcanvas
python -m venv venv
```
Activate the environment:
* **Windows**: `.\venv\Scripts\activate`
* **macOS/Linux**: `source venv/bin/activate`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Create a `.env` file in the project root with the following parameters:
```env
SECRET_KEY=your-cryptographically-secure-key
MAIL_USERNAME=your-smtp-email@gmail.com
MAIL_PASSWORD=your-app-specific-email-password
MAIL_DEFAULT_SENDER=your-smtp-email@gmail.com
BALLCHASING_TOKEN=your-ballchasing-api-key
```
*Note: A Ballchasing API token can be generated under your account profile page on ballchasing.com.*

### 4. Build and Seed the Database
Initialize and seed the SQLite database with official car models and hitbox classes:
```bash
python seed_hitboxes.py
```

### 5. Launch the Application
Run the local secure Flask server:
```bash
python app.py
```
Open `https://localhost:5000` in your browser. (Accept the self-signed certificate warning for local development if prompted).

---

## Developer Info

* **Author**: Greg Kotelnikov
* **License**: MIT License
