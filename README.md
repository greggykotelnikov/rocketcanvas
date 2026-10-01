# RocketCanvas

A web application built for Rocket League players who want more than a stats page. RocketCanvas pulls match history from the Ballchasing API, lets you build and save custom car presets, explore hitbox geometry in 3D, generate positional heatmaps from raw `.replay` files, and install as a PWA on desktop or mobile. The whole thing runs over HTTPS with proper authentication baked in from the start.

---

## Features

### Dashboard and Match History
Search any Rocket League player name to fetch their 50 most recent replays from Ballchasing. Each match is labelled as a win or loss based on which team the player appeared on, and their goal differential is calculated automatically.

### Analytics
A dedicated analytics page that processes the same replay data and breaks it down into a set of charts:
- Win rate over time (rolling 5-game window)
- Map-specific win rates (top 6 maps by games played)
- Playlist distribution
- Hourly activity breakdown (what time of day you play most)
- Goal differential per match
- Average goals scored vs conceded
- Cumulative win progression
- Current win/loss streak and all-time best/worst

### Positional Heatmaps
Users can upload a raw `.replay` file directly from their Rocket League installation. The backend runs it through `rrrocket` (a binary that parses the proprietary replay format) and extracts X/Y positional data for each player frame by frame. The frontend renders these positions as a colour-coded density heatmap overlaid on a top-down pitch diagram using HTML5 Canvas.

### 3D Hitbox Visualiser
An interactive 3D wireframe tool that renders all six official Rocket League hitbox classes (Octane, Dominus, Breakout, Hybrid, Plank and Merc) using HTML5 Canvas with manual geometry and vector math. The user can rotate the hitbox in real time using yaw and pitch controls. Telemetry stats and exact hitbox dimensions are displayed alongside the render. There is also a searchable lookup table that maps car names to their hitbox class.

### Screenshot Hitbox Recogniser (experimental)
On the hitbox page, drop in a screenshot of a car and an image classifier guesses its hitbox class, showing the top three guesses with confidence bars and example cars. The model is a Google Teachable Machine MobileNetV2 classifier, exported to ONNX and run with `onnxruntime`, so the app does not need TensorFlow. The bundled model is heavily biased toward Octane; see [Retraining the hitbox classifier](#retraining-the-hitbox-classifier).

### 2D Garage Builder
A layered sprite editor that lets users build a car visually by stacking image layers across five categories: body, chassis, additions, patches and effects. The end result can be exported and submitted to the gallery.

### Trading Card Gallery
A shared gallery where users can upload screenshots of their car presets and display them as stylised trading cards. Five card templates are available: Legendary, Golden, Chroma Sparkle, Carbon Fiber and Holographic. Each card shows the user's avatar, username and a custom overlay title.

### Car Recommendation Tool
A simple recommendation page that suggests car bodies based on the user's current competitive rank and preferred hitbox type.

### Guided Tours with TTS Audio
Every page includes an interactive guided tour narrated using the browser's Web Speech API, with procedural audio synthesis for UI sound effects. Tours are persona-based and walk users through the page's features step by step.

### Progressive Web App
RocketCanvas is installable as a PWA. A registered service worker handles offline caching so the app remains accessible when the network drops. The manifest enables home screen installation on both desktop and mobile.

---

## Technology Stack


| Layer | Technologies |
|---|---|
| Backend | Python 3.11, Flask |
| Database | SQLite via Flask-SQLAlchemy |
| Authentication | Flask-Login, Flask-Bcrypt, Flask-Mail (email-based 2FA codes) |
| Frontend | Vanilla HTML/CSS/JavaScript, HTML5 Canvas |
| Charts | Chart.js |
| Image Processing | Pillow |
| Replay Parsing | rrrocket v0.11.6 (auto-downloaded for Windows, macOS or Linux) |
| API | ballchasing.com REST API |
| Security | Flask-WTF (CSRF), Flask-Limiter (rate limiting) |
| PWA | Web Audio API, Service Workers, Web App Manifest |

---

## Security Architecture

Authentication uses a two-factor flow. After submitting a valid email and password, the user is redirected to a verification page where they must enter a 6-digit code sent to their email. The code expires after 10 minutes and is invalidated on use. Old unused codes are also invalidated when a new one is issued.

Beyond authentication, the following security controls are applied:

- **CSRF protection**: All POST routes are protected by WTForms CSRF tokens via Flask-WTF.
- **Content Security Policy**: A per-request cryptographic nonce (`g.nonce`) is injected into all `<script>` and `<style>` tags and included in the CSP header to block inline XSS.
- **Security headers**: HSTS, X-Frame-Options (DENY), X-Content-Type-Options (nosniff), X-XSS-Protection (set to 0, per OWASP), Referrer-Policy and Permissions-Policy are all applied via a custom WSGI middleware layer.
- **Session hardening**: Cookies are set with `HTTPOnly`, `Secure` and `SameSite=Lax`.
- **Rate limiting**: Flask-Limiter applies a global limit of 300 requests per day and 60 per hour, with stricter per-route limits on login and register.
- **Password hashing**: Bcrypt with automatic salting.
- **Avatar validation**: Uploaded images are validated by extension and then re-encoded via Pillow. They are cropped to a square and resized to 256x256 pixels before saving, preventing oversized or malformed files from being stored as-is.
- **Server version suppression**: Werkzeug's default server version header is removed to avoid leaking version information.

---

## File Structure

```
rocketcanvas/
├── app.py                  # Main Flask application, all routes, security middleware
├── auth.py                 # Register, login and 2FA verification flow
├── models.py               # SQLAlchemy models: User, TwoFactorCode, CarHitbox, CarDesign
├── ballchasing.py          # Wrapper for the ballchasing.com REST API
├── replay_parser.py        # Parses .replay files via rrrocket, extracts player positions
├── hitbox_classifier.py    # Screenshot -> hitbox class inference (onnxruntime)
├── seed_hitboxes.py        # Seeds the database with official car hitbox data
├── ml/                     # Classifier model (.h5 + ONNX), labels and training script
├── scripts/                # Dev helpers: SRI hashes, model conversion, sample replay
├── tests/                  # pytest suite
├── requirements.txt        # Python package dependencies
├── templates/
│   ├── base.html           # Shared layout, navigation, theme controls, footer
│   ├── login.html          # Login and registration form (single page, mode-switched)
│   ├── verify.html         # 2FA code entry screen
│   ├── profile.html        # Account settings, platform link, avatar management
│   ├── dashboard.html      # Player search and match history feed
│   ├── analytics.html      # Multi-chart performance breakdown
│   ├── heatmap.html        # Replay upload and heatmap renderer
│   ├── hitbox.html         # 3D hitbox visualiser and car lookup table
│   ├── garage.html         # Layered 2D car builder
│   ├── gallery.html        # Trading card gallery and design uploader
│   ├── recommend.html      # Car recommendation tool
│   └── offline.html        # Service worker offline fallback
├── static/
│   ├── css/                # Stylesheets (dialogue boxes, trading cards, loading screens)
│   ├── js/                 # Client-side scripts (music player, canvas effects, tour guide, charts)
│   ├── sounds/             # Audio assets and ambient loops
│   ├── images/             # Icons, backgrounds and builder layer sprites
│   ├── manifest.json       # PWA web app manifest
│   ├── sw.js               # Service worker for offline caching
│   └── uploads/            # User-uploaded avatars and car design images
└── bin/                    # Auto-downloaded rrrocket binary (created at runtime)
```

---

## Database Models

### User
Stores account credentials and profile info.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| email | String(120) | Unique |
| username | String(80) | Unique |
| password_hash | String(200) | Bcrypt hash |
| rl_username | String(80) | Optional Rocket League in-game name |
| rank | String(50) | Self-reported competitive rank |
| bio | String(300) | Profile bio, capped at 300 characters |
| avatar_url | String(200) | Filename of stored avatar image |
| platform | String(50) | PC, PlayStation, Xbox, etc. |
| created_at | DateTime | Account creation timestamp |

### TwoFactorCode
Temporary 2FA codes tied to a user and login session.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User |
| code | String(6) | 6-digit numeric code |
| expires_at | DateTime | 10 minutes from issue |
| used | Boolean | Invalidated after first use |

### CarHitbox
Stores the hitbox class for each car name. Seeded by `seed_hitboxes.py`.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| car_name | String(100) | Unique car display name |
| hitbox_class | String(50) | One of: Octane, Dominus, Breakout, Hybrid, Plank, Merc |

### CarDesign
User-submitted car design images displayed in the gallery.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User |
| title | String(150) | Design title |
| image_filename | String(255) | Stored filename (UUID-based) |
| card_template | String(50) | Visual style: legendary, golden, chroma, carbon, holographic |
| overlay_title | String(100) | Optional text shown on the card face |
| created_at | DateTime | Upload timestamp |

---

## API Routes

| Method | Route | Auth | Description |
|---|---|---|---|
| GET | `/` | No | Redirects to `/login` |
| GET/POST | `/register` | No | Create a new account |
| GET/POST | `/login` | No | Log in with email and password |
| GET/POST | `/verify` | No | Submit 2FA code |
| POST | `/logout` | Yes | Log out and clear session (CSRF-protected) |
| GET | `/profile` | Yes | View profile page |
| POST | `/profile/update` | Yes | Update username, rank, bio, platform |
| POST | `/profile/avatar` | Yes | Upload and crop a custom avatar |
| POST | `/profile/avatar/preset` | Yes | Select a preset avatar |
| POST | `/link-rl` | Yes | Save Rocket League in-game name |
| GET | `/dashboard` | Yes | Search player and view match history |
| GET | `/analytics` | Yes | View performance analytics charts |
| GET/POST | `/hitbox` | Yes | Look up car hitbox class |
| GET | `/heatmap` | Yes | View heatmap page |
| POST | `/parse-replay` | Yes | Upload `.replay` file and receive position data |
| POST | `/hitbox/recognise` | Yes | Upload a car screenshot and receive hitbox guesses |
| POST | `/gallery/<id>/delete` | Yes | Delete one of your own gallery designs |
| POST | `/verify/resend` | No | Send a fresh 2FA code for the login in progress |
| GET | `/garage` | Yes | Open the 2D garage builder |
| GET | `/gallery` | Yes | Browse trading card gallery |
| POST | `/gallery/upload` | Yes | Submit a new car design |
| GET | `/recommend` | Yes | Car recommendation tool |
| GET | `/manifest.json` | No | PWA manifest |
| GET | `/sw.js` | No | Service worker script |
| GET | `/offline` | No | Offline fallback page |

---

## Replay Parsing

The `/parse-replay` endpoint accepts a `.replay` file uploaded from the browser. The file is saved to a temporary location and passed to `replay_parser.py`, which calls `rrrocket` as a subprocess. `rrrocket` is a purpose-built binary that decodes Rocket League's proprietary binary replay format and outputs structured JSON.

The parser then walks through every network frame in the JSON output, tracking:
- Which actor IDs correspond to players (via `PRI_TA` / `PlayerReplicationInfo` object names)
- Which actor IDs correspond to cars (`Car_Default`)
- How cars are linked to players (via `PlayerReplicationInfo` references on the car actor)
- The 3D location of each car at each frame (via `ReplicatedRBState`)

The X and Y coordinates (in centimetres) are extracted and returned as a dictionary mapping each player's name to their list of positional samples. The frontend renders these samples as a density heatmap on a Canvas element.

`rrrocket` is automatically downloaded from GitHub at runtime if the binary is not already present in the `bin/` directory. The correct build for the host (Windows x64, Linux x64, macOS Intel or Apple Silicon) is chosen automatically, its SHA-256 checksum is verified against a pinned value, and the download is guarded by a lock.

---

## Retraining the hitbox classifier

1. Collect in-game screenshots into one folder per class: `ml/hitbox_images/{octane,dominus,hybrid,merc,plank,breakout}/`. Aim for a similar number per class (at least ~50 each). The folder is git-ignored.
2. Create a separate environment for TensorFlow (not needed to run the app):
   ```bash
   python -m venv mlenv
   mlenv/Scripts/pip install -r requirements-ml.txt
   ```
3. Train and export:
   ```bash
   mlenv/Scripts/python ml/train_hitbox_model.py
   ```
   This writes `ml/keras_model.h5` and `ml/hitbox_classifier.onnx`. Restart the app to pick up the new model.

`scripts/convert_model_to_onnx.py` re-exports an existing `.h5` (for example a new Teachable Machine download) without retraining.

---

## Installation

### Prerequisites
- Python 3.11+
- A modern browser (Chrome, Edge or Firefox recommended)
- (Optional) `mkcert` for local HTTPS certificates

HTTPS is optional for local development. Without certificates the app serves plain HTTP on `http://localhost:5000`; browsers treat `localhost` as a secure context, so service workers, the Web Audio API and login cookies all still work.

To use HTTPS instead, generate local certificates with:
```bash
mkcert localhost 127.0.0.1 ::1
```
and place `localhost+2.pem` and `localhost+2-key.pem` in the project root (or set `SSL_CERT_FILE` / `SSL_KEY_FILE` in `.env`). These files are git-ignored: never commit a private key.

### 1. Clone and set up a virtual environment
```bash
git clone https://github.com/greggykotelnikov/rocketcanvas.git
cd rocketcanvas
python -m venv venv
```
Activate it:
- **Windows**: `.\venv\Scripts\activate`
- **macOS/Linux**: `source venv/bin/activate`

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-cryptographically-secure-key
MAIL_USERNAME=your-smtp-email@gmail.com
MAIL_PASSWORD=your-app-specific-email-password
MAIL_DEFAULT_SENDER=your-smtp-email@gmail.com
BALLCHASING_API_KEY=your-ballchasing-api-key
```
A Ballchasing API key can be generated on your profile page at [ballchasing.com](https://ballchasing.com).

### 4. Seed the database (automatic)
The hitbox table is populated automatically the first time the app starts. After adding cars to `seed_hitboxes.py`, run it to insert the new ones into an existing database:
```bash
python seed_hitboxes.py
```

### 5. Run the server
```bash
python app.py
```
Open `http://localhost:5000` (or `https://localhost:5000` if you set up certificates) in your browser.

### 6. Run the tests
```bash
pip install -r requirements-dev.txt
python -m pytest
```
The suite uses an in-memory SQLite database, captures 2FA emails instead of sending them and mocks the Ballchasing API, so no `.env` is needed.

---

## Known Limitations

- **Replay parsing platforms**: `rrrocket` builds exist for Windows x64, Linux x64 and macOS (Intel and Apple Silicon). Other platforms (e.g. Linux on ARM) cannot parse replays.
- **Browser requirements**: A modern browser is required for HTML5 Canvas rendering, the Web Audio API and service workers. The app will not function correctly in older or unsupported browsers.
- **SQLite**: The database is a local SQLite file and is not suitable for multi-instance or production deployments without switching to PostgreSQL or similar.
- **Ballchasing API dependency**: Dashboard and analytics features require a valid Ballchasing API key. Without one, the dashboard shows a 'missing Ballchasing API key' message.
- **No email provider fallback**: 2FA codes are sent via Gmail SMTP. If SMTP credentials are not configured the login flow will break entirely, as users cannot complete verification without receiving their code.

---

## Developer Info

**Author**: Greg Kotelnikov  
**License**: MIT
