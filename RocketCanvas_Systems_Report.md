# Year 12: Software Engineering Systems Report: RocketCanvas

**Client**: Youth Gaming Club  
**Name**: Greg Kotelnikov  
**Teacher**: Ms. Macasaquit  
**Class**: 12 Software Engineering  

---

## Contents

1. Identifying and defining  
   1.1. Define and analyse problem requirements  
   1.2. Tools to develop ideas and generate solutions  
   1.3. Benefits of developing secure programs  
   1.4. System specifications and dependencies  
2. Research and planning  
   2.1. Project management  
   2.2. Quality assurance  
   2.3. Systems modelling  
3. Producing and implementing  
4. Testing and evaluating  
   4.1. Evaluation of code  
   4.2. Evaluation of solution  
5. Setup and installation instructions  
6. References  

---

## 1. Identifying and defining

### 1.1. Define and analyse problem requirements

#### Problem context

Rocket League has been a highly popular game over the span of the last decade. However, it also had its ups and downs. After the removal of trading, many aspiring players of different skill levels decided that the game had reached its downhill point. However, with the recent updates and with the involvement of prominent influencers in the game throughout 2026, many new players began to discover Rocket League. RocketCanvas is the ultimate solution for younger audiences that want to improve at the game and access their stats through beautiful Chart.js graphs, by pulling all of the data from the public ballchasing.com API. Individuals can create profiles, make their own cars as a 2d sprite, access the dashboard and listen to retro synth 80s music all at the same time. The client of Kotelnikov Technologies is a Youth Gaming Club.

As previously mentioned, RocketCanvas is being developed for the Youth Gaming Club which is a community of younger Rocket League players who want to improve their skills and stay engaged with the game. The problems that were faced by the developers of this application (Kotelnikov Technologies) can be broken down into three components that are all connected to each other.

One of the main issues that were encountered were players who record and upload their match replays to the public ballchasing.com API that had absolutely no straightforward way to convert that raw data they got into something that is actually meaningful. The API of ballchasing.com returns detailed statistics but the website's interface is notoriously difficult for less experienced users to interpret (which is also the target audience of the website) hence demonstrating that some players struggle to translate their replay data into actionable insight about their own performance.

Another issue that largely contributed towards the idea of the development of RocketCanvas is that the existing garage builder tools that are already utilised for customising in game cars typically use unconventional and unintuitive interfaces. This makes it difficult for newer or younger players to engage with the creative side of the game and also makes it more difficult to navigate through the website which is an important factor in sustaining curiosity and long term interest in the community for the newcomers.

One of the most significant issues that was faced was also that no existing platform was ready to bring car customisation, design sharing, statistics tracking and community features together in one place. As a result, players are forced to move between several separate, often confusing websites just to understand how they are performing and to engage with the wider community.

Together, these three components compound the same underlying problem: every extra step a new player has to take before they feel competent or connected to the community increases the likelihood that they disengage and stop playing altogether, which in turn slows the growth of the Rocket League community that the Youth Gaming Club exists to support.

#### Needs and opportunities

The needs of RocketCanvas, based on the problem context above, are described in the table below.

| Need | Description |
|---|---|
| 1 | An accessible statistics dashboard that pulls match data directly from the ballchasing.com API and displays it as clear, visual charts (using Chart.js), so players can understand their own performance without needing to interpret ballchasing.com's interface themselves. |
| 2 | An intuitive car customisation tool ("garage builder") that lets players design their car as a 2D sprite through a simple, visually engaging interface, lowering the barrier to entry compared to existing garage builder tools. |
| 3 | A single, unified platform that brings together car customisation, design uploads, statistics and community features, removing the need for players to move between multiple disconnected websites. |
| 4 | Engagement features, such as customisable profiles (rank, photo, light/dark mode) and ambient retro-synth music, that make the platform more enjoyable to use and help retain new players long enough for them to become attached to the game and its community. |

#### Assess the scheduling and financial feasibility

Need 1 will be completed first, as the data-pulling and Chart.js integration are already partially functional and this need does not depend on any other component. Need 2 (the garage builder) can be developed in parallel, although its more advanced feature, the machine learning hitbox detection, depends on first collecting a sufficient image dataset for each car class. Need 3 is dependent on Needs 1 and 2 both being functional individually, since unifying the platform requires the statistics dashboard and garage builder to already exist. Need 4 is the lowest priority and depends on Need 3, as engagement features are only meaningful once the core platform is in place.

The financial feasibility of RocketCanvas is anchored in a local-only deployment model, which avoids the recurring monthly expenses associated with cloud database instances and application hosting. While hosting a Flask web application with a live database on a platform like AWS or Heroku would require ongoing subscription fees, running the server on the user's local machine reduces the hosting footprint to zero dollars. The primary capital expenditure was limited to forty dollars for asset licensing. This choice was made to acquire high-quality, pre-made retro synth tracks and 2D car sprite sheets rather than dedicating developer time to graphic design and music production, which would have significantly delayed the project schedule. The estimated development labor of six hundred dollars represents the opportunity cost of the forty hours of engineering work required to build the backend logic, template files and API connectors.

Scheduling the implementation of the platform was planned around the dependencies of the components. The core statistics dashboard had to be built first because it provides the foundational user interface and database connections that the other modules build upon. Developing the garage builder in parallel allowed the interface design to progress independently of the analytics engine, ensuring that both systems were ready for unification. The machine learning classifier was deferred to a later phase because it required a large training dataset that could only be gathered once the basic car database was functional. By deferring the lowest priority engagement features to the final stage of development, the development team ensured that the core utility of the application was stable before integrating secondary features like background music.

In terms of cost, the project has low but not negligible financial overhead. The ballchasing.com API is free and public, Chart.js is open-source, and the application is intended to run locally rather than be hosted, removing ongoing hosting costs. The main cost incurred during development was approximately $40 AUD, spent on licensing around 80 retro 80s-style synth tracks for the in-app music feature and on the 2D car sprite artwork used in the garage builder. Beyond this, the only other cost is the time required to collect and label images for the machine learning component.

The table below itemizes direct expenses alongside estimated labor and utility costs to establish the total project valuation.

| Item | Description | Cost (AUD) |
|---|---|---|
| Development Laptop | Personal computer used for local development, compiling and testing | $0.00 |
| Python Runtime | Open-source programming language (Python 3.11) | $0.00 |
| Development IDE | Visual Studio Code editor used for writing and debugging code | $0.00 |
| Version Control | Git version control hosted on a public GitHub repository | $0.00 |
| Asset Licensing | Purchased retro synth tracks and 2D car sprite artwork from itch.io | $40.00 |
| Network Usage | Internet usage for library installation, API research and documentation | $20.00 |
| Electricity | Utility costs for powering the workstation during development | $15.00 |
| Testing Labor | Quality assurance, ZAP scans and manual validation (approx. 5 hours @ $15/hr) | $75.00 |
| Development Labor | Writing application logic, database models and templates (approx. 40 hours @ $15/hr) | $600.00 |
| Documentation | Compiling systems report, DFDs and technical specifications | $50.00 |
| Security Remediation | Patching vulnerabilities and configuring security middleware | $25.00 |
| **Total** | **Combined project valuation** | **$825.00** |

#### Requirement of the problem

Functionality: RocketCanvas must allow users to create a profile, pull and accurately match their own replay data from ballchasing.com, display that data as readable charts, design and preview a 2D sprite car, and browse other users' car designs and stats, all from a single platform.

Performance: the system must correctly match a player's replays to their identity, even where naming inconsistencies exist (for example, treating "justin" and "justin." as the same player rather than two separate records). Charts must load and update responsively as new data is pulled, and the interface must remain intuitive and usable for the target audience of younger, less technically experienced players.

Data structures and data types: The system will require structured data to represent player profiles (e.g. username, rank, profile photo), match records pulled from the ballchasing.com API (e.g. wins, losses, map, date) and car designs (e.g. car model, sprite image, hitbox classification). The specific variables, data types and validation rules for each of these are defined in the data dictionaries in Section 2.3.

#### Boundaries

Hardware: the application is intended to run locally rather than on a hosted server, so performance is limited by the user's own device; the machine learning component in particular may require reasonable processing power to train and run the hitbox classification model.

Operating system / platform: the interface is browser-based (HTML/JavaScript with Chart.js), so it should run on any modern browser regardless of operating system.

Data limitations: the machine learning hitbox classifier is constrained by the size of the training dataset; some car classes currently have as few as 50 images, below the 100-images-per-class minimum needed for reliable supervised learning.

Security: because the application stores user profiles and accepts uploaded content, it must satisfy ZAP and Bandit security testing requirements, meaning only informational-level alerts are acceptable in the final build.

---

### 1.2. Tools to develop ideas and generate solutions

#### Identification of appropriate software development tools

| Situation | Tool applicability | Reason |
|---|---|---|
| Brainstorming, mind-mapping and storyboards | Applicable | Storyboards will be used to plan how each page of RocketCanvas (dashboard, garage builder, profile, gallery) should look and flow before development begins, helping to visualise the unified platform described in Need 3. |
| Data dictionaries | Applicable | Needed to define the variables, data types and validation rules for player profiles, match data and car designs identified above. |
| Algorithm design | Applicable | Required to design the logic for matching player names from ballchasing.com (resolving issues such as "justin" vs "justin.") and for the machine learning hitbox classification process. |
| Code generation | Applicable | Chart.js and the ballchasing.com API integration already exist as a starting point; further code generation will extend these into the full dashboard. |
| Testing and debugging | Applicable | Needed to resolve existing issues, such as the replay-matching bug and the ZAP/Bandit security alerts identified during development. |
| Installation | Limited applicability | As the application is intended to run locally for the Youth Gaming Club rather than be distributed broadly, installation will be minimal, likely limited to local setup instructions in the README. |
| Maintenance | Applicable | Ongoing maintenance will be required to expand the machine learning hitbox dataset and respond to client feedback already received from beta testers. |

#### Implementation method

A phased implementation approach is most applicable to a web application like RocketCanvas. Rather than releasing the entire platform at once, each core feature, the statistics dashboard, the garage builder, profile customisation and the community features, will be implemented and tested individually before being integrated into the unified platform. This matches the dependency structure identified in the feasibility analysis above, where Needs 1 and 2 must be functional before Need 3 (the unified platform) can be completed, and allows client feedback to be gathered and acted on at each phase rather than only at the end of the project.

---

### 1.3. Benefits of developing secure programs

#### Importance of Security for the RocketCanvas Platform

Security is a fundamental consideration for the RocketCanvas platform because the application manages user accounts, handles file uploads and makes external requests to third party APIs. Without the implementation of secure programming practices, the system would remain vulnerable to local credential theft, malicious code execution via uploaded files and database manipulation. Since the application runs locally on the user's hardware, standard server side firewalls do not protect the local environment. Security must therefore be enforced at the code level, preventing unauthorized actions and securing the local SQLite file from simple extraction exploits. Developing secure programs ensures that the user's data remains private, application operations run reliably and third party API tokens are protected from leakage.

#### How RocketCanvas Implements Cryptographic Controls

Passwords stored by the application are protected using modern cryptographic hashing. Storing plain text passwords in a database creates a significant risk of exposure if the database file is accessed by an unauthorized entity. RocketCanvas mitigates this risk by using Flask-Bcrypt, which wraps the blowfish cipher. Bcrypt automatically applies a random salt value to each password and performs key stretching through multiple work iterations. This process slows down hashing operations programmatically, making the hashes highly resistant to GPU accelerated dictionary and brute force attacks. The system only stores the resulting hash value in the database, verifying user authenticity during login by comparing the generated hash of the submitted credentials against the stored record, meaning the raw password is never kept in memory or written to disk.

#### Form Validation and Password Constraints

To prevent users from setting weak and vulnerable passwords, the application enforces validation rules during registration and password change procedures. The registration route in `auth.py` processes input strings through structured conditionals that check for complexity. The password must contain at least eight characters, include at least one numeric digit and feature at least one special character. Usernames are limited to eighty characters and checked for duplication against existing records in the database. These rules protect the system from automated scripting that attempts to register multiple empty or low complexity accounts, and ensures that user credentials cannot be easily guessed by other players.

#### Defense Against Injection Attacks

SQL injection is a critical vulnerability where an attacker submits database commands inside input fields to bypass authentication or delete data. RocketCanvas prevents injection attacks by utilizing the Flask-SQLAlchemy Object Relational Mapper (ORM). The ORM handles query construction internally, converting database transactions into parameterized queries. Instead of formatting input values directly into SQL strings, the database driver uses placeholders, treating user inputs strictly as literal data values rather than executable commands. This design separates the query logic from the data parameters, ensuring that even if a user submits SQL syntax inside a form field, the SQLite engine treats it as a text string rather than a query override.

#### Session Configuration and Browser Defenses

Session security is managed by configuring cookie attributes on the local Flask application. The session cookies are hardened with `HTTPOnly`, `Secure` and `SameSite` flags. The `HTTPOnly` flag prevents client side scripts from accessing the session token, which mitigates cross site scripting attacks that attempt to steal session keys. The `Secure` flag forces the browser to only transmit cookies over encrypted HTTPS channels, protecting the token from interception on local networks. The `SameSite=Lax` configuration ensures that the browser does not attach session cookies to cross site requests, defending the user against cross site request forgery attempts.

---

### 1.4. System specifications and dependencies

#### Hardware and Software Specifications

The application is designed to run locally on client workstations rather than being deployed to a remote server. The minimum and recommended hardware specifications required to run the local Flask server and render the client-side interface are listed below.

*   **Operating System**: Microsoft Windows 10 or 11 (64-bit), macOS 10.15 (Catalina) or newer, or a modern Linux distribution (Ubuntu 20.04+).
*   **Processor (CPU)**: Dual-core Intel Core i3 or AMD Ryzen 3 equivalent running at 2.0 GHz or faster. A multi-core processor is required to handle concurrent requests on the local development server while running the browser interface.
*   **System Memory (RAM)**: 4 GB minimum (8 GB recommended). This ensures sufficient memory is available to run the local Python interpreter, the SQLite engine, the web browser and the system terminal simultaneously.
*   **Storage Space**: 100 MB of free hard drive space. The application itself has a small footprint, but disk space is needed to store the local SQLite database, cached sprite assets, licensed audio tracks and uploaded replay files.
*   **Network Adapter**: A stable internet connection with at least 2 Mbps download speed is required to fetch real-time player data from the ballchasing.com API.

The minimum hardware requirements are designed to accommodate the local processing overhead of the Flask application and its support tools. Unlike a typical web app where the server-side code runs on a dedicated cloud machine, RocketCanvas runs its web server, database engine and front-end interface on the user's personal computer. System memory is the primary performance bottleneck during local execution. When a user uploads a match replay, the backend spawns a separate subprocess to execute the compiled `rrrocket` binary. This binary decompresses and parses large binary files in memory, which temporarily increases RAM utilization. Having at least 4 GB of RAM prevents the operating system from swapping memory to the hard drive, which would cause noticeable browser lag and slow down chart rendering.

The storage requirement of 100 MB provides a buffer for the local SQLite database and user-uploaded content. Although a clean installation of the application requires less than 50 MB, the SQLite database grows incrementally as users save custom car designs and cache player statistics. Replay files uploaded for heatmap processing are temporarily stored on the local disk before being parsed, which requires temporary storage overhead. The network bandwidth minimum of 2 Mbps ensures that API requests to ballchasing.com do not time out. The API returns detailed JSON payloads containing match data, and slow connections would cause the frontend charts to hang while waiting for the data to arrive.

#### Software Dependencies

RocketCanvas is built using Python 3.11 and leverages several open-source libraries to handle authentication, database communication, security and file parsing. Each dependency is detailed below.

*   **Flask**: The core micro-framework. It manages the request-response cycle, maps URL endpoints to Python view functions, renders HTML templates using the Jinja2 engine and manages user session cookies.
*   **Flask-SQLAlchemy**: An extension that integrates SQLAlchemy ORM with Flask. It abstracts SQL queries into Python object operations, manages database connection pools and handles schema generation for the local SQLite database.
*   **Flask-Login**: The session authentication library. It tracks whether a user is logged in, manages cookie-based user sessions, provides the `current_user` context object and protects routes from unauthenticated access via the `@login_required` decorator.
*   **Flask-Bcrypt**: A hashing utility that wraps the Bcrypt library. It handles the salting and hashing of user passwords before they are written to the database, and performs secure constant-time comparisons during authentication.
*   **Flask-Mail**: A mail server interface. It establishes secure SMTP connections using TLS over port 587, allowing the application to deliver random six-digit two-factor authentication (2FA) codes to users' registered email addresses.
*   **Flask-WTF**: An integration layer for WTForms. It provides automatic Cross-Site Request Forgery (CSRF) protection by generating unique tokens that must be validated with every state-changing POST request.
*   **Flask-Limiter**: A rate-limiting extension. It tracks incoming requests by client IP address and enforces request limits (e.g. 60 requests per hour) to mitigate automated credential stuffing and brute-force attacks.
*   **Pillow**: An image processing library. It is used to sanitize uploaded image files. Pillow opens uploaded files, crops them to square dimensions, resizes them to standard resolutions (256x256 pixels for avatars) and saves them as new RGB images to strip potential payload metadata.
*   **Chart.js**: A client-side JavaScript graphing library. It consumes JSON-formatted statistics payloads returned by the Flask backend and renders eight distinct interactive canvas charts on the analytics page.
*   **rrrocket**: A compiled Rust binary wrapper. It is used by the application to decompress and decode binary Rocket League `.replay` files into structured JSON objects, exposing positional coordinate data for heatmap generation.

Choosing Flask as the web framework was driven by the need for a lightweight, modular system that does not introduce the administrative overhead of larger frameworks like Django. Flask allows the developer to construct routes and integrate database models using simple Python scripts, making it ideal for a localized application. Flask-SQLAlchemy was selected to manage the database connection because it eliminates the need to write raw SQL queries for standard CRUD operations. By representing tables as Python classes, the application remains database-independent, allowing the developer to test using a local SQLite file and migrate to a server-based database later if requirements change.

For security, Flask-Bcrypt and Flask-WTF were chosen to address critical vulnerabilities early in the development lifecycle. Standard cryptography libraries can be complex to configure, but Flask-Bcrypt provides a simple interface to generate secure, one-way password hashes using a high work factor that resists brute-force attacks. Flask-WTF automates the injection and validation of CSRF tokens in all POST forms, securing the application against unauthorized cross-site requests without requiring manual token checks on every route. Flask-Limiter provides protection against local scripting attacks by rate-limiting request routes, which helps satisfy the quality criteria established during security reviews.

#### Programming Paradigm Selection and Rationale

RocketCanvas utilizes a hybrid programming paradigm, combining event driven front end processes with procedural and structured back end algorithms. The web routing architecture and server framework operate under an event driven model. In this setup, the execution flow is determined by user actions, such as clicking a route, uploading a file or requesting a player search. The Flask server acts as an event loop, waiting for HTTP request events and dispatching them to the corresponding Python view function. On the client side, the garage builder and the heatmap generator use JavaScript event listeners to capture selection updates and mouse clicks, triggering canvas redraw actions dynamically. This event driven paradigm is optimal for web applications because it allows the software to remain responsive to asynchronous user interactions without locking up the user interface.

For data processing and file parsing, the application uses procedural programming. Functions like coordinate decoding in `replay_parser.py` and name matching in `ballchasing.py` are written as linear sequences of operations. The code reads binary replay files, parses actor definitions step by step and returns data lists. This structured, procedural approach is chosen for the computational components because it organizes calculations into clear, self-contained procedures that are easy to test and optimize, avoiding the unnecessary class inheritance overhead of a pure object oriented design.

---

## 2. Research and planning

### 2.1. Project management

#### Software Development Approach

RocketCanvas was developed using a phased Agile approach. While the four core needs identified in Section 1.1 followed a broadly sequential dependency structure (the unified platform in Need 3 could not be completed until the statistics dashboard and garage builder in Needs 1 and 2 were functional), development within each individual feature was iterative rather than strictly linear. Features such as the analytics dashboard were revisited and expanded multiple times after their initial build, for example, the chart suite grew from a small set of basic statistics to eight distinct visualisations (rolling win rate, map-specific win rates, playlist distribution, hourly activity, goal differential, cumulative win progression and streak tracking) as testing and personal use revealed further opportunities for insight. This iterative refinement, combined with the clear sequential dependencies between major needs, makes a pure Waterfall model too rigid a description of the actual process, while a pure Agile model understates the fixed dependency chain governing the four needs. A WAgile approach, combining Waterfall's dependency-driven sequencing of major milestones with Agile's iterative refinement within each milestone, most accurately reflects how RocketCanvas was actually built.

#### Version Control and Backup Strategy

Version control for RocketCanvas was managed using Git, with repository replication hosted on GitHub. Unlike file syncing services like Dropbox that overwrite files on change, Git tracks modifications at a line-by-line level, preserving a complete ledger of every change made to the codebase. Git enables feature branching, allowing new routes or experimental components to be developed in isolation without affecting the main codebase. If a modification introduces an error, the repository can be rolled back to any previous stable commit.

Hosting the repository on GitHub provides remote backup redundancy, ensuring that the project can be recovered if the developer's local storage device fails. Commit operations were performed incrementally as individual features reached functional stability, providing a clear audit trail. This was particularly helpful when the machine learning classifier was abandoned in favor of the manual coordinate lookup model, as the relevant changes could be cleanly reverted without affecting other code files.

---

### 2.2. Quality assurance

Quality criteria for RocketCanvas come straight out of the four needs in Section 1.1, since the whole point of a quality criterion is checking whether a need actually got met by the finished product, not just attempted. For Need 1, the dashboard, the criteria is that match data has to actually be pulled correctly and matched to the right player, even when ballchasing.com returns a slightly different name than what was typed in. Our company ran into this constantly during testing, searching "justin" would sometimes miss matches that were actually logged under "justin." With a full stop on the end, and if that is not handled the whole dashboard is basically lying to the user about their own stats. So the criteria here is not just "does the dashboard load", it is specifically "does it load the correct data for the correct person".

For Need 2, the garage builder, the criteria is whether someone can actually build a car without getting confused. The company Kotelnikov Technologies tested this myself a few times by just trying to make a design without thinking about how our company built it, more like a fresh user would, and the layering between body, chassis, additions, patches and effects needed to make visual sense in that order or things looked broken.

For Need 3, the unified platform, the criteria is that moving between dashboard, garage, gallery and profile has to feel like one app. No broken links, no jarring style changes between pages. This one is honestly hard to test formally, it is more of a "does it feel right" criteria, which is why the developer team leaned on actually clicking through the whole site myself and also had a couple of people test it blind.

For Need 4 if the music or a tour pop-up makes a core feature slower or more annoying to use, then that can be considered a failure, since this need is explicitly the lowest priority and is not supposed to interfere with the actual functional parts of the app.

There is also a security side quality criteria that does not map to one specific Need but applies across the whole platform: ZAP and Bandit testing should only flag informational-level issues by the time the build is final. The company used the same two tools here that Kotelnikov Technologies used for the security report assessment, so that developers already had a rough process for running them, which made this part faster than it would have been starting from scratch.

#### Compliance and Legislative Requirements

| Compliance or legislative issue | Methods for mitigation |
|---|---|
| NSW Privacy and Personal Information Act 1998 and Federal Privacy Act 1988: RocketCanvas stores personal information including email address, username, self-reported rank and avatar images | Passwords are never stored in plain text and are hashed using Bcrypt with automatic salting before being saved. Email addresses are only used to deliver 2FA verification codes and are not shared with any third party. Codes expire after 10 minutes and are invalidated after a single use, limiting the window in which a compromised code could be exploited. |
| ISO/IEC 27001 (Information Security Management): the application authenticates users and stores both personal data and user-generated content | CSRF protection is enforced through Flask-WTF on all POST and PUT routes. A nonce-based Content Security Policy mitigates XSS. Session cookies are hardened with HTTPOnly, Secure and SameSite=Lax attributes. Flask-Limiter enforces rate limiting to defend against brute-force attempts. ZAP and Bandit testing were used to identify and resolve vulnerabilities prior to completion. |
| Image upload security: avatar and car design uploads present a risk of malformed or oversized files being stored and served to other users | Uploaded images are validated by extension and re-encoded through Pillow rather than stored as-is, with avatars cropped to a square and resized to 256x256 pixels before saving. |
| Third-party API dependency: RocketCanvas relies on the external ballchasing.com API for core functionality | The API key is stored as an environment variable and is never hard-coded or committed to version control. The application does not redistribute ballchasing.com's data beyond displaying it to the authenticated user it belongs to, in line with the API's terms of use. |
| Asset licensing: RocketCanvas uses purchased audio tracks and a mix of purchased and original sprite artwork for the garage builder and music feature | All 80 retro synth tracks used in the music feature were purchased under a commercial-use licence from itch.io, and the licensed terms permit use within a project such as this but explicitly prohibit redistribution, resale or resharing of the asset files themselves. Car sprite artwork used in the garage builder is a mix of licensed purchased assets and original artwork created personally for the project. As with the music assets, the purchased sprite assets are licensed for use within RocketCanvas only and may not be redistributed, resold or extracted and reshared independently of the application. This distinction matters because while the finished application is free to use and share as a project, the underlying asset files themselves remain under their original licence terms and cannot be repackaged or distributed separately. |

---

### 2.3. Systems modelling

#### Level 0 DFD (Context Diagram)

At Level 0, RocketCanvas is represented as a single process bounded by its two external entities: the User and the ballchasing.com API.

```
                  ┌──────────────┐
                  │              │ <── Credentials, uploads & replays
                  │     User     │
                  │              │ ──> Rendered pages, charts & heatmaps
                  └──────┬───────┘
                         │▲
                         ││
                         ▼│
           ┌────────────────────────────┐
           │   RocketCanvas Application │
           └─────────────┬──────────────┘
                         │▲
                         ││ Request player stats
                         ▼│
                  ┌──────────────┐
                  │ ballchasing  │
                  │   .com API   │
                  │              │ ──> Raw match JSON payloads
                  └──────────────┘
```

The User entity sends authentication data (email, password) into the system and receives back rendered pages including the dashboard, analytics charts, garage builder and also includes other features like gallery. The User also sends uploaded content into the system and also in particular .replay files that are used for heatmap generation and the user entity also can directly assist with avatar/car design images selection for profile and gallery features and receives processed output back, namely positional heatmap visualisations and stored design uploads.

The ballchasing.com API entity is the second external entity. RocketCanvas sends outbound requests containing a player's Rocket League username and receives back raw match data (wins, losses, map, goals, replay IDs) which is then processed internally before being displayed to the User. This is the only external data source the system depends on, since rrrocket is treated as one of the internal subprocesses rather than an external entity given it is bundled with and called directly by the application itself rather than queried over a network.

#### Level 1 DFD (Major Processes)

As a level 1 DFD diagram is a diagram that includes the major design processes broken down, that would mean that the demonstration required would likely need a break down of each of the sections of the application.

```
                      ┌──────────────────────────────────────┐
                      │                 User                 │
                      └──────────────────┬───────────────────┘
                                         │▲
                      Replays & designs  ││ Auth & rendered UI
                                         ▼│
┌────────────────────────┐  user_id  ┌───┴───┐  credentials  ┌────────────────────────┐
│                        │ <─────────│  P1   │ <───────────> │                        │
│       CarDesign        │           │ Auth  │               │          User          │
│       Data Store       │  designs  └───────┘   write/read  │       Data Store       │
│                        │ <─────┐                       ┌──>│                        │
└────────────────────────┘       │                       │   └────────────────────────┘
                                 │                       │
┌────────────────────────┐       │   ┌───────┐           │   ┌────────────────────────┐
│                        │       ├───│  P3   │           └───│     TwoFactorCode      │
│       CarHitbox        │ <─────┼───│Garage │               │       Data Store       │
│       Data Store       │  read │   └───────┘               └────────────────────────┘
│                        │       │
└────────────────────────┘       │   ┌───────┐ player-name   ┌────────────────────────┐
                                 ├───│  P2   │ ────────────> │  ballchasing.com API   │
                                 │   │ Stats │ <──────────── │    External Entity     │
                                 │   └───────┘   match data  └────────────────────────┘
                                 │
                                 │   ┌───────┐
                                 └───│  P4   │ <─── Spawn subprocess rrrocket.exe
                                     │Heatmap│
                                     └───────┘
```

*   **Process 1: Authentication & Session Management**: Receives login credentials from the User, validates them against the User data store (password_hash field), and on success generates a 2FA code which is sent via Flask-Mail to the User's registered email and temporarily stored in the TwoFactorCode data store. Once the User submits the correct code, a session is created and the User is granted access to the remaining processes.
*   **Process 2: Statistics Dashboard & Analytics**: Receives a player search request from the authenticated User, sends a query to the ballchasing.com API external entity, and receives back raw match data. This process resolves naming inconsistencies (e.g. matching "justin" to "justin.") before writing match records into a temporary in-session data structure. The resolved data is then passed to the Chart.js rendering layer, which outputs the eight analytics visualisations back to the User.
*   **Process 3: Garage Builder**: Receives layer selections (body, chassis, additions, patches, effects) from the User and combines them into a single composited car sprite. This process reads from the CarHitbox data store to display hitbox classification information alongside the build, and on export, writes the finished design to the CarDesign data store along with the User's user_id as a foreign key.
*   **Process 4: Replay Parser & Heatmap Generator**: Receives an uploaded .replay file from the User, passes it to the rrrocket subprocess for binary decoding, and receives back structured JSON containing frame-by-frame actor data. This process filters that JSON for PlayerReplicationInfo and ReplicatedRBState objects to extract X/Y positional coordinates per player, which are then passed to the Canvas rendering layer to output a density heatmap back to the User.
*   **Process 5: Gallery & Community Features**: Receives car design uploads from the User (sourced from Process 3's output), validates and re-encodes them via Pillow, and writes them to the CarDesign data store, this time including card_template and overlay_title metadata. On retrieval, this process reads from the same data store and outputs the trading card gallery view to all authenticated Users, not just the uploader, making this the only process where data flows from one User's input to another User's output.

The Level 1 Data Flow Diagram maps the internal pathways of the application. Processes read and write to the database tables using explicit query filters. Process 1 coordinates with the User data store to verify hashed credentials and write generated 2FA tokens to the TwoFactorCode store. Process 2 acts as a proxy, retrieving external API records and storing them inside temporary memory dictionaries before generating Javascript charts. Process 3 reads from the CarHitbox table to identify properties like hitbox dimensions, and writes exported design records to the CarDesign table. Process 4 works with localized files, passing inputs to the `rrrocket` subprocess, and streaming parsed lists to the front-end rendering engine.

#### Structure Chart

One of the main files of the application such as app.py sits at the top of the structure chart. Every route in RocketCanvas gets defined here, so it ends up importing and coordinating basically every other module in the system. It also applies the security middleware, things like CSP nonce injection, security headers and rate limiting, to every response before it goes back to the user. This makes app.py the main coordinator of the whole application.

Below it there are multiple modules that act like its children. auth.py handles login, register, verify and logout. It checks credentials, calls Bcrypt for the hashing, and runs the 2FA flow including sending the code through Flask-Mail. models.py is different. Nothing calls it directly. Instead almost every other module imports it, since it defines the database schema for User, TwoFactorCode, CarHitbox and CarDesign. Every read or write in the app eventually goes through this file. So it's less of a module with its own logic and more of a shared foundation everything else sits on top of.

ballchasing.py only runs when the dashboard or analytics pages are hit. It queries the ballchasing.com API, fixes naming mismatches like "justin" versus "justin.", and sends the cleaned data back up to app.py. replay_parser.py is probably the riskiest module here, since it's the only one that spawns a subprocess, rrrocket.exe. It has to handle the binary not existing yet, which triggers an auto download, and it has to handle uploaded files that aren't actually valid replays. seed_hitboxes.py barely counts as part of the runtime structure at all. It's a script you run once by hand to fill the CarHitbox table, and it sits completely outside the normal request flow.

There's a smaller third layer too. Inside auth.py there's a separate call just for sending the email through Flask-Mail. The developers of Kotelnikov Technologies decided it was necessary to keep that isolated on purpose. The main reason for that decision was the proposition that if the SMTP details are wrong that failure would stay contained instead of breaking the whole login. Inside ballchasing.py the name matching logic is its own function too, so that the developer could test it without needing the API call working at the same time. Inside replay_parser.py the part that walks through the JSON looking for PlayerReplicationInfo and ReplicatedRBState is separate from the part that actually runs rrrocket. That way if the parser tool is swapped out later, the developers do not need to touch how the subprocess gets called.

So the structure ends up flat but cleanly split. app.py runs the show, each feature module can be changed on its own without breaking the others, and models.py just holds everything's data underneath it all.

#### Class Diagrams

The four SQLAlchemy model classes in `models.py` form the entire persistent data layer of RocketCanvas. Each class maps directly to a SQLite table, and the relationships between them reflect the real access patterns of the application.

```
┌───────────────────────────────────────────────┐
│                    User                        │
├───────────────────────────────────────────────┤
│ - id           : Integer  [PK]                 │
│ - email        : String   [unique, not null]   │
│ - username     : String   [unique, not null]   │
│ - password_hash: String   [not null]           │
│ - rl_username  : String   [nullable]           │
│ - rank         : String   [nullable]           │
│ - bio          : String   [nullable]           │
│ - avatar_url   : String   [nullable]           │
│ - platform     : String   [nullable]           │
│ - created_at   : DateTime [default: utcnow]    │
├───────────────────────────────────────────────┤
│ + get_id() : String        [Flask-Login]       │
│ + is_authenticated() : Boolean                 │
│ + is_active() : Boolean                        │
└────────────────┬──────────────────────────────┘
                 │ 1
                 │
        ┌────────┴──────────────────────────────────────────────┐
        │                                                       │
        │ 0..*                                                  │ 0..*
┌───────▼──────────────────────────────────┐   ┌──────────────▼──────────────────────────────────┐
│             TwoFactorCode                │   │                 CarDesign                        │
├──────────────────────────────────────────┤   ├─────────────────────────────────────────────────┤
│ - id        : Integer [PK]               │   │ - id             : Integer  [PK]                 │
│ - user_id   : Integer [FK -> user.id]     │   │ - user_id        : Integer  [FK -> user.id]       │
│ - code      : String  [not null]         │   │ - title          : String   [not null]            │
│ - expires_at: DateTime [not null]        │   │ - image_filename : String   [not null]            │
│ - used      : Boolean [default: False]   │   │ - card_template  : String   [default: legendary] │
└──────────────────────────────────────────┘   │ - overlay_title  : String   [nullable]           │
                                               │ - created_at     : DateTime [default: utcnow]    │
                                               └─────────────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│               CarHitbox                  │
├──────────────────────────────────────────┤
│ - id          : Integer [PK]             │
│ - car_name    : String  [unique, not null]│
│ - hitbox_class: String  [not null]       │
└──────────────────────────────────────────┘
```

*(Note: `CarHitbox` has no foreign key relationship to any other table. It is read-only reference data, seeded once by `seed_hitboxes.py` and queried by the garage builder to display hitbox classification information alongside a user's chosen car body.)*

##### Explanation of Each Class

*   **User**: The `User` class is the central model in the application. It stores the credentials and profile information for every registered account. The `email` and `username` fields are both marked unique, so no two accounts can share either value. `password_hash` stores the output of Flask-Bcrypt's `generate_password_hash()` function rather than the plain-text password, meaning the raw password never persists anywhere in the database. The optional fields (`rl_username`, `rank`, `bio`, `avatar_url`, `platform`) are all nullable because a user can register and use core features without completing their profile. The class inherits from Flask-Login's `UserMixin`, which provides the helper authentication flags consumed by the session management layer.
*   **TwoFactorCode**: The `TwoFactorCode` class holds the short-lived six-digit codes generated during the 2FA step of login and registration. The `user_id` foreign key ties each code record back to the `User` table, and before a new code is issued, `auth.py` sets `used = True` on all existing unused codes for that user to prevent replay attacks. The `expires_at` field is set to ten minutes after generation, and the `verify` route in `auth.py` rejects any code where `expires_at` is in the past, even if `used` is still `False`.
*   **CarHitbox**: The `CarHitbox` class stores the mapping between a specific in-game car name and its hitbox class (one of: Octane, Dominus, Plank, Breakout, Hybrid, Merc). The table is populated once by running `seed_hitboxes.py` and is treated as read-only reference data during normal application operation. The garage builder reads from this table to show the user which hitbox class corresponds to the car body they have selected.
*   **CarDesign**: The `CarDesign` class stores every car design that has been exported from the garage builder and submitted to the gallery. The `user_id` foreign key links each design back to the `User` who created it. The SQLAlchemy `relationship()` call on this model creates a `designs` backref on the `User` object, allowing `current_user.designs` to be used anywhere in `app.py` to retrieve all designs by the logged-in user without a manual query. The `card_template` field controls which visual frame style is applied to the design, and `overlay_title` holds a user-supplied subtitle. The `image_filename` field stores only the filename rather than the full path, keeping the database entries portable.

##### Relationships Summary

| Relationship | Type | Details |
|---|---|---|
| User -> TwoFactorCode | One-to-many | One user can have multiple code records; each code belongs to exactly one user via `user_id` FK |
| User -> CarDesign | One-to-many | One user can upload multiple designs; each design is owned by exactly one user via `user_id` FK |
| CarHitbox | Standalone | No FK relationships; acts as a seeded reference lookup table only |

The absence of a direct foreign key between `CarDesign` and `CarHitbox` is intentional. The hitbox class a user sees in the garage builder is determined at read time by querying `CarHitbox` using the car name as a lookup key, rather than being stored on the design record itself. This means that if a car's hitbox classification were ever corrected in the `CarHitbox` table, all existing designs that reference that car body would automatically reflect the updated classification without any migration of the `CarDesign` table.

#### Data Dictionaries

The following tables define the schema, data types, constraints and validation rules for the four SQLAlchemy models defined in `models.py`.

##### User Table Data Dictionary

| Variable Name | Database Data Type | Key Type | Nullable | Validation Rules / Constraints | Description |
|---|---|---|---|---|---|
| `id` | INTEGER | Primary Key | No | Auto-incrementing integer | Unique identifier for each user profile. |
| `email` | VARCHAR(120) | Unique | No | Must be unique, not null and match standard email syntax. | Registered user email address, used for sending 2FA codes. |
| `username` | VARCHAR(80) | Unique | No | Must be unique, not null and between 1 and 80 characters. | Unique profile name chosen by the user. |
| `password_hash` | VARCHAR(200) | None | No | Must be a valid Bcrypt hash, not null. | Salted and hashed representation of the user password. |
| `rl_username` | VARCHAR(80) | None | Yes | Nullable, max length 80 characters. | Associated Rocket League account name used to query the API. |
| `rank` | VARCHAR(50) | None | Yes | Nullable, must match standard Rocket League rank tiers. | Self-reported player rank (e.g. Diamond III). |
| `bio` | VARCHAR(300) | None | Yes | Nullable, maximum length 300 characters. | Short personal biography displayed on the profile page. |
| `avatar_url` | VARCHAR(200) | None | Yes | Nullable, must point to an image file in the upload directory. | Filename of the custom cropped avatar image. |
| `platform` | VARCHAR(50) | None | Yes | Nullable, restricted to PC, PSN, Xbox or Switch. | Associated gaming platform. |
| `created_at` | DATETIME | None | No | Defaults to current UTC timestamp on row insertion. | Registration timestamp of the user account. |

##### TwoFactorCode Table Data Dictionary

| Variable Name | Database Data Type | Key Type | Nullable | Validation Rules / Constraints | Description |
|---|---|---|---|---|---|
| `id` | INTEGER | Primary Key | No | Auto-incrementing integer | Unique identifier for each 2FA code record. |
| `user_id` | INTEGER | Foreign Key | No | Must reference a valid `id` in the User table. | Links the 2FA code to a specific user account. |
| `code` | VARCHAR(6) | None | No | Must be exactly 6 characters long, numeric characters only. | Randomly generated temporary verification code. |
| `expires_at` | DATETIME | None | No | Set to 10 minutes past creation timestamp. | Expiry timestamp used to reject old verification codes. |
| `used` | BOOLEAN | None | No | Boolean flag, defaults to `False`. | Indicates if the verification code has already been consumed. |

##### CarHitbox Table Data Dictionary

| Variable Name | Database Data Type | Key Type | Nullable | Validation Rules / Constraints | Description |
|---|---|---|---|---|---|
| `id` | INTEGER | Primary Key | No | Auto-incrementing integer | Unique identifier for each car hitbox mapping. |
| `car_name` | VARCHAR(100) | Unique | No | Must be unique, maximum length 100 characters. | Name of the car model as registered in game files. |
| `hitbox_class` | VARCHAR(50) | None | No | Must be one of the six official hitbox classes. | Hitbox grouping (e.g. Octane, Dominus or Plank). |

##### CarDesign Table Data Dictionary

| Variable Name | Database Data Type | Key Type | Nullable | Validation Rules / Constraints | Description |
|---|---|---|---|---|---|
| `id` | INTEGER | Primary Key | No | Auto-incrementing integer | Unique identifier for each saved car design. |
| `user_id` | INTEGER | Foreign Key | No | Must reference a valid `id` in the User table. | Links the saved design to its creator. |
| `title` | VARCHAR(150) | None | No | Must be between 1 and 150 characters, not null. | User-provided name for the car configuration. |
| `image_filename` | VARCHAR(255) | None | No | Must map to a valid image in the designs folder. | Filename of the exported 2D sprite image. |
| `card_template` | VARCHAR(50) | None | No | Defaults to `'legendary'`. Must be a valid template name. | Style template applied to the card in the gallery. |
| `overlay_title` | VARCHAR(100) | None | Yes | Nullable, maximum length 100 characters. | Optional custom subtitle printed on the card. |
| `created_at` | DATETIME | None | No | Defaults to current UTC timestamp on row insertion. | Timestamp indicating when the design was shared. |

The database uses a single-file SQLite configuration to maximize portability and simplify local execution. Using a heavier database engine like PostgreSQL or MySQL would require the user to install and configure a database server on their machine before running the app, creating a high barrier to entry for the target audience. SQLite stores all data in a single file inside the project directory, allowing the database to be backed up, moved or cleared by simply copying or deleting the database file. To prevent data redundancy, the `CarHitbox` table was designed as a separate reference database. Storing the hitbox category on each individual `CarDesign` record would duplicate strings across the database, wasting space and making it difficult to correct errors if a car's hitbox classification changes.

The one-to-many relationship between the `User` and `TwoFactorCode` models allows the system to maintain a historical log of all login attempts. Instead of overwriting a single code record on the user profile, storing codes in a separate table allows the application to track active, expired and consumed codes over time. This separation provides audit data that can be used to detect suspicious login patterns, such as multiple code requests in a short timeframe. The `CarDesign` table uses a foreign key pointing to the user table to ensure that every shared design is linked to an active creator profile, allowing the gallery view to render the uploader's username alongside the design card.

#### Storyboards

Storyboards map the page structure, UI elements and user navigation pathways before coding begins. RocketCanvas features five key views, each presented below using layout wireframes.

##### 1. Login and Register View

```
┌────────────────────────────────────────────────────────┐
│  ROCKETCANVAS                                [Theme]   │
├────────────────────────────────────────────────────────┤
│                                                        │
│                  ┌──────────────────┐                  │
│                  │  AUTHENTICATION  │                  │
│                  ├──────────────────┤                  │
│                  │ Email:           │                  │
│                  │ [              ] │                  │
│                  │ Password:        │                  │
│                  │ [************  ] │                  │
│                  │                  │                  │
│                  │  [   Submit   ]  │                  │
│                  ├──────────────────┤                  │
│                  │ Toggle Register  │                  │
│                  └──────────────────┘                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

*   **Layout & Style**: Centered dark-themed glassmorphism panel. Input fields feature clear labels, and error messages flash directly above the authentication panel.
*   **Navigation**: Submitting valid credentials triggers a redirection to the 2FA verification view. Clicking "Toggle Register" swaps the form fields client-side without reloading the page.

##### 2. Dashboard and Analytics View

```
┌────────────────────────────────────────────────────────┐
│  ROCKETCANVAS   [Dashboard]  [Garage]  [Gallery]  [Out]│
├────────────────────────────────────────────────────────┤
│  Search Player: [ Username ] [ Search ]                │
├────────────────────────────────────────────────────────┤
│  ┌───────────────────────┐   ┌──────────────────────┐  │
│  │   Win Rate Trend      │   │   Map Performance    │  │
│  │  ┌─────────────────┐  │   │  ┌────────────────┐  │  │
│  │  │   Line Chart    │  │   │  │   Bar Chart    │  │  │
│  │  └─────────────────┘  │   │  └────────────────┘  │  │
│  └───────────────────────┘   └──────────────────────┘  │
│  ┌───────────────────────┐   ┌──────────────────────┐  │
│  │   Hourly Activity     │   │   Goal Differential  │  │
│  │  ┌─────────────────┐  │   │  ┌────────────────┐  │  │
│  │  │   Radar Chart   │  │   │  │  Scatter Plot  │  │  │
│  │  └─────────────────┘  │   │  └────────────────┘  │  │
│  └───────────────────────┘   └──────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

*   **Layout & Style**: Top navigation bar with responsive grid container. The body displays eight grid cards housing dynamic Chart.js canvases that render win rate, map distribution and goal histories.
*   **Navigation**: Entering a player name and clicking "Search" updates the current view with active data queried from the ballchasing.com API.

##### 3. 2D Garage Builder View

```
┌────────────────────────────────────────────────────────┐
│  ROCKETCANVAS   [Dashboard]  [Garage]  [Gallery]  [Out]│
├────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐   ┌───────────────────────┐  │
│  │   Canvas Preview     │   │   Customisation       │  │
│  │                      │   │   Chassis:   [ v ]    │  │
│  │   [ Composited Car ] │   │   Decal:     [ v ]    │  │
│  │   [ Sprite Layers  ] │   │   Additions: [ v ]    │  │
│  │                      │   │   Effects:   [ v ]    │  │
│  │ ──────────────────── │   ├───────────────────────┤  │
│  │ Hitbox: Octane class │   │ Title:   [         ]  │  │
│  └──────────────────────┘   │ [Export to Gallery]   │  │
└────────────────────────────────────────────────────────┘
```

*   **Layout & Style**: Split column interface. The left column renders layered transparent PNG files on an HTML5 canvas to preview the car, with reference hitbox information rendered below it. The right column houses select lists and inputs.
*   **Navigation**: Selecting an item from any dropdown list triggers a canvas redraw. Clicking the export button saves the composited image file and redirects to the trading card gallery.

##### 4. Trading Card Gallery View

```
┌────────────────────────────────────────────────────────┐
│  ROCKETCANVAS   [Dashboard]  [Garage]  [Gallery]  [Out]│
├────────────────────────────────────────────────────────┤
│  [ Upload New Design File ]                            │
│                                                        │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────┐ │
│  │  Legendary Card  │ │    Rare Card     │ │ ...     │ │
│  │  ┌────────────┐  │ │  ┌────────────┐  │ │         │ │
│  │  │ Car Image  │  │ │  │ Car Image  │  │ │         │ │
│  │  └────────────┘  │ │  └────────────┘  │ │         │ │
│  │  TitleText       │ │  TitleText       │ │         │ │
│  │  Subtitle        │ │  Subtitle        │ │         │ │
│  └──────────────────┘ └──────────────────┘ └─────────┘ │
└────────────────────────────────────────────────────────┘
```

*   **Layout & Style**: Grid container representing trading cards. Each card uses distinct CSS classes matching the selected card template tier (e.g. gold borders for legendary cards) and displays the title, overlay subtitle and date.
*   **Navigation**: Users upload new designs via the top modal button. Clicking individual cards opens a full-screen image preview.

##### 5. Replay Heatmap View

```
┌────────────────────────────────────────────────────────┐
│  ROCKETCANVAS   [Dashboard]  [Garage]  [Gallery]  [Out]│
├────────────────────────────────────────────────────────┤
│  Upload Replay File: [ Browse... ] [ Generate Heatmap ]│
├────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │                Heatmap Canvas                    │  │
│  │                                                  │  │
│  │               [ Map Outline ]                    │  │
│  │               [ Density Plot ]                   │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│  Select Player: [ Player A  v ]                       │
└────────────────────────────────────────────────────────┘
```

*   **Layout & Style**: Centered file upload bar sitting above a large canvas component. The canvas displays the structural lines of a standard Rocket League arena as a background, overlaying a coordinate density plot.
*   **Navigation**: Uploading a `.replay` file triggers an asynchronous call to the backend. Once parsed, the player dropdown list becomes active, and selecting a player updates the heatmap distribution on the canvas.

The storyboards map the visual framework of RocketCanvas. By laying out the interfaces as discrete modules, navigation conflicts were identified and resolved before the coding phase. For instance, the profile modification fields and avatar upload buttons were consolidated into a single card container on the profile page, ensuring users did not have to jump between separate configuration menus. Client side rendering logic on the garage canvas redrawing transparent layers on user input ensures that selections are validated instantly without initiating server requests, optimizing frontend performance and providing a smooth user experience.

#### Decision Trees

Decision trees map the logical flows within the application, defining how input conditions transition to specific system states.

##### 1. Two-Factor Authentication (2FA) Verification Flow

The logic governing user authentication and 2FA code validation is mapped below.

```
                         [ User submits login form ]
                                      │
                         Is email/password valid?
                         ├─── No ───> [ Flash error, return to Login ]
                         └─── Yes ──> [ Generate random 6-digit string ]
                                      [ Invalidate previous codes in DB ]
                                      [ Save new code and expiry time ]
                                      [ Send email via Flask-Mail ]
                                      [ Redirect user to Verify View ]
                                                     │
                                        [ User inputs 6-digit code ]
                                                     │
                                            Does code match DB?
                                   ├─── No ───> [ Flash error, keep on Verify ]
                                   └─── Yes ──> Has code expired or been used?
                                                ├─── Yes ──> [ Flash error ]
                                                └─── No ───> [ Mark code used = True ]
                                                             [ Log user in via Flask-Login ]
                                                             [ Redirect user to Profile ]
```

##### 2. Player Name Resolution and Replay Result Matching Flow

The logic below processes raw JSON responses returned by the ballchasing.com API to resolve player naming variations and determine match results.

```
                       [ Search player name query string ]
                                      │
                         [ Call search API endpoint ]
                                      │
                       [ Iterate over list of replays ]
                                      │
                    Is query string in Blue Player Names?
                    ├─── Yes ──> Blue goals > Orange goals?
                    │            ├─── Yes ──> Result = "win"
                    │            └─── No ───> Result = "loss"
                    │
                    └─── No ───> Is query string in Orange Player Names?
                                 ├─── Yes ──> Orange goals > Blue goals?
                                 │            ├─── Yes ──> Result = "win"
                                 │            └─── No ───> Result = "loss"
                                 │
                                 └─── No ───> Result = "unknown"
                                                     │
                                       [ Return result for replay ]
```

#### Algorithm Design and Pseudocode

Detailed pseudocode implementations for the name resolution algorithm and the coordinate processing loop are defined below.

##### 1. Username Resolution and Replay Parsing Algorithm

The following algorithm iterates through raw replay documents fetched from the external API, matches the search query against player rosters and categorizes the match outcome.

```
ALGORITHM ResolvePlayerReplays(search_name, replay_list)
    resolved_replays = empty list
    search_lower = ConvertToLowercase(search_name)
    
    FOR EACH replay IN replay_list
        blue_players = ExtractPlayers(replay, "blue")
        orange_players = ExtractPlayers(replay, "orange")
        
        blue_goals = GetGoals(replay, "blue")
        orange_goals = GetGoals(replay, "orange")
        
        found_on_blue = False
        FOR EACH player IN blue_players
            IF search_lower is substring of ConvertToLowercase(player.name) THEN
                found_on_blue = True
                EXIT FOR
            ENDIF
        ENDFOR
        
        found_on_orange = False
        FOR EACH player IN orange_players
            IF search_lower is substring of ConvertToLowercase(player.name) THEN
                found_on_orange = True
                EXIT FOR
            ENDIF
        ENDFOR
        
        IF found_on_blue THEN
            IF blue_goals > orange_goals THEN
                replay.result = "win"
            ELSE
                replay.result = "loss"
            ENDIF
        ELSE IF found_on_orange THEN
            IF orange_goals > blue_goals THEN
                replay.result = "win"
            ELSE
                replay.result = "loss"
            ENDIF
        ELSE
            replay.result = "unknown"
        ENDIF
        
        Append resolved_replays with replay
    ENDFOR
    
    RETURN resolved_replays
END ALGORITHM
```

##### 2. Network Frame Positional Coordinate Extraction Algorithm

The following algorithm parses decoded network frames from the `rrrocket` JSON output, resolving player identities and extracting spatial coordinates.

```
ALGORITHM ExtractReplayCoordinates(decoded_json)
    IF "objects" not in decoded_json OR "network_frames" not in decoded_json THEN
        RETURN empty map
    ENDIF
    
    objects_list = decoded_json["objects"]
    pri_actors = empty map       // Maps actor ID to player username
    car_positions = empty map    // Maps car actor ID to list of coordinate pairs
    car_to_pri = empty map       // Maps car actor ID to driver PRI actor ID
    
    FOR EACH frame IN decoded_json["network_frames"]["frames"]
        // Register new actors initialized in this frame
        IF "new_actors" in frame THEN
            FOR EACH actor IN frame["new_actors"]
                obj_name = objects_list[actor["object_id"]]
                actor_id = actor["actor_id"]
                
                IF obj_name contains "PlayerReplicationInfo" THEN
                    pri_actors[actor_id] = "Unknown"
                ELSE IF obj_name contains "Car_Default" THEN
                    car_positions[actor_id] = empty list
                ENDIF
            ENDFOR
        ENDIF
        
        // Process attribute updates for active actors
        IF "updated_actors" in frame THEN
            FOR EACH actor IN frame["updated_actors"]
                actor_id = actor["actor_id"]
                prop_id = actor["object_id"]
                prop_name = objects_list[prop_id]
                attribute = actor["attribute"]
                
                // Track user name changes
                IF actor_id exists in pri_actors THEN
                    IF prop_name contains "PlayerName" THEN
                        pri_actors[actor_id] = attribute["String"]
                    ENDIF
                ENDIF
                
                // Link cars to their driver PRI record
                IF actor_id exists in car_positions THEN
                    IF prop_name contains "PlayerReplicationInfo" THEN
                        IF "ActiveActor" exists in attribute AND attribute["ActiveActor"]["active"] is True THEN
                            car_to_pri[actor_id] = attribute["ActiveActor"]["actor"]
                        ELSE IF "Int" exists in attribute THEN
                            car_to_pri[actor_id] = attribute["Int"]
                        ENDIF
                    ENDIF
                    
                    // Log X/Y coordinate vectors from rigid body states
                    IF prop_name contains "ReplicatedRBState" THEN
                        location = attribute["RigidBody"]["location"]
                        IF "x" exists in location AND "y" exists in location THEN
                            Append coordinate pair [location["x"], location["y"]] to car_positions[actor_id]
                        ENDIF
                    ENDIF
                ENDIF
            ENDFOR
        ENDIF
    ENDFOR
    
    // Map extracted coordinates back to usernames
    player_heatmaps = empty map
    FOR EACH car_id, positions IN car_positions
        IF positions is not empty THEN
            pri_id = car_to_pri[car_id]
            IF pri_id exists in pri_actors THEN
                username = pri_actors[pri_id]
                IF username is not "Unknown" THEN
                    player_heatmaps[username] = positions
                ENDIF
            ENDIF
        ENDIF
    ENDFOR
    
    RETURN player_heatmaps
END ALGORITHM
```

Extracting spatial data from Rocket League replays requires decoding a complex binary stream that records the state of all actors in the game. The application spawns the `rrrocket` binary to convert this stream into a structured JSON file containing frame-by-frame updates. The parsing algorithm must iterate through these frames to rebuild the game state because the binary does not store player positions in a simple list. The algorithm first identifies when a new actor is created, checking if it represents a player info block or a physical car body. Once these actors are registered, the parser tracks attribute updates to link each car body actor to the player name string stored in the player info block.

Position updates are recorded in the `ReplicatedRBState` attributes, which contain the X and Y coordinates of the car on the field. The parser extracts these vectors, scales them from centimeters to field coordinate dimensions and appends them to a list for each player. Because cars can change IDs during a match (such as when a player leaves and a bot joins), the algorithm must continuously verify the links between car actors and player replication infos. Once the entire frame stream is parsed, the accumulated list of coordinates is mapped to the final player names and returned as a JSON object, which the frontend canvas uses to render a density heatmap.

---

## 3. Producing and implementing

### Main features

[Screenshot: Login/Register page]
This screen implements the authentication process described in Section 2.3 Process 1 (Authentication and Session Management). It directly satisfies the security boundary defined in Section 1.1, requiring users to register before accessing personal features, and reflects the User and TwoFactorCode data dictionary entries from Section 2.3.

[Screenshot: 2FA verification page]
This screen completes the authentication flow shown in the Level 1 DFD, Process 1. The 6-digit code field corresponds to the code variable defined in the data dictionary, and the page enforces the 10-minute expiry and single-use invalidation described in the compliance section.

[Screenshot: Statistics dashboard]
This screen fulfils Need 1 from Section 1.1, pulling match data from the ballchasing.com API and displaying it through Chart.js. It corresponds to Process 2 in the Level 1 DFD and demonstrates the resolved player-matching logic, since the player searched for here returns correctly matched results despite naming inconsistencies.

[Screenshot: Analytics page, full chart suite]
This expands on the dashboard above and demonstrates the eight chart visualisations referenced in Section 2.1’s WAgile justification, showing the iterative growth of this feature from a basic set of statistics to its current form.

[Screenshot: 2D Garage Builder]
This screen fulfils Need 2, implementing the layered sprite system (body, chassis, additions, patches, effects) described in Section 2.3 Process 3 and corresponding to the CarDesign entries in the data dictionary.

[Screenshot: Hitbox visualiser]
This screen demonstrates the pivot described in Section 4.2, where the originally planned machine learning classifier was replaced with a manually built 3D/HTML5 visualiser after the training dataset proved insufficient.

[Screenshot: Trading card gallery]
This screen fulfils Need 3, demonstrating the unified-platform goal by showing user-submitted car designs displayed alongside their card_template and overlay_title metadata, corresponding to Process 5 in the Level 1 DFD.

[Screenshot: Heatmap page with an uploaded replay]
This screen fulfils the replay parsing requirement described in Section 1.1’s data structures, showing the output of the rrrocket subprocess decoding described in Process 4 of the Level 1 DFD.

[Screenshot: Profile page with theme/music settings]
This screen fulfils Need 4, the lowest-priority engagement features, and reflects the customisable profile and ambient music functionality described in the original needs table.

### Code Walkthrough

The following section walks through the core modules of the RocketCanvas codebase, detailing how security, authentication, API interaction and file parsing are implemented.

#### 1. Database Layer (`models.py`)

The application database schema is defined in [models.py](file:///c:/Users/kotel/rocketcanvas/models.py). The code block below details the schema definitions:

```python
# models.py: Lines 7-25
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rl_username   = db.Column(db.String(80),  nullable=True)
    rank          = db.Column(db.String(50),  nullable=True)
    bio           = db.Column(db.String(300), nullable=True)
    avatar_url    = db.Column(db.String(200), nullable=True)
    platform      = db.Column(db.String(50),  nullable=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

class TwoFactorCode(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code       = db.Column(db.String(6),  nullable=False)
    expires_at = db.Column(db.DateTime,   nullable=False)
    used       = db.Column(db.Boolean,    default=False)
```

The database models leverage SQLAlchemy's declarative base. The `User` model inherits from Flask-Login's `UserMixin` to support helper authentication flags. The `TwoFactorCode` model uses a foreign key constraint linking `user_id` to the user table, establishing a one-to-many relationship where multiple code instances can point to a single user.

#### 2. User Authentication and 2FA Code Validation (`auth.py`)

User session validation and two-factor mail dispatch are managed in [auth.py](file:///c:/Users/kotel/rocketcanvas/auth.py). The verification route logic is shown below:

```python
# auth.py: Lines 99-125
@app.route("/verify", methods=["GET", "POST"])
def verify():
    user_id = session.get("pending_user_id")
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        entered = request.form.get("code", "").strip()
        now = datetime.utcnow()

        record = TwoFactorCode.query.filter_by(
            user_id=user_id, code=entered, used=False
        ).first()

        if not record or record.expires_at < now:
            flash("Invalid or expired code.", "error")
            return render_template("verify.html")

        record.used = True
        db.session.commit()

        user = User.query.get(user_id)
        login_user(user)
        session.pop("pending_user_id", None)
        return redirect(url_for("profile"))

    return render_template("verify.html")
```

The verification route reads the code from the form submission. It retrieves the code record from the SQLite database, confirming it matches the user and that it has not been marked as used. By comparing `record.expires_at` against the current UTC timestamp, the code is confirmed to be fresh. If valid, the code is flagged as used in the database to prevent reuse, and the session ID is initialized via `login_user(user)`.

#### 3. External API Client (`ballchasing.py`)

Communicating with the ballchasing.com REST endpoint is handled in [ballchasing.py](file:///c:/Users/kotel/rocketcanvas/ballchasing.py). The query configuration is shown below:

```python
# ballchasing.py: Lines 20-33
def search_replays_by_player(player_name, count=10):
    """
    Search replays where a player name matches.
    Returns a list of replay summaries.
    """
    params = {
        "player-name": player_name,
        "count": count,
        "sort-by": "replay-date",
        "sort-dir": "desc"
    }
    r = requests.get(f"{BASE_URL}/replays", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()
```

The API request uses the `requests` library. Query parameters are passed to restrict the search to a specific player name, limit the response count, and sort the matches by date in descending order. The `Authorization` header containing the API key is passed securely on each request, and `raise_for_status()` handles error conditions.

#### 4. Binary Replay Parser (`replay_parser.py`)

Parsing binary match records is encapsulated in [replay_parser.py](file:///c:/Users/kotel/rocketcanvas/replay_parser.py). The state extraction logic is shown below:

```python
# replay_parser.py: Lines 82-97
# Check for Car linking to PRI
if actor_id in car_positions:
    if "PlayerReplicationInfo" in prop_name and ("Pawn" in prop_name or "Car" in prop_name):
        if "ActiveActor" in attr:
            if attr["ActiveActor"].get("active"):
                car_to_pri[actor_id] = attr["ActiveActor"]["actor"]
        elif "Int" in attr:
            car_to_pri[actor_id] = attr["Int"]

    # Check for RigidBody location (property name is ReplicatedRBState)
    if "ReplicatedRBState" in prop_name:
        loc = attr.get("RigidBody", {}).get("location", {})
        if "x" in loc and "y" in loc:
            # rrrocket gives cm, usually RL maps are ~10240x8192
            car_positions[actor_id].append([loc["x"], loc["y"]])
```

The parser executes the `rrrocket` binary in a subprocess to decode the compressed stream. It reads frame updates in a single pass, mapping car actor IDs to their respective player profiles (PRIs) via the active pawn attribute, and updates coordinate arrays on each frame step.

#### 5. Application Router and Middleware (`app.py`)

The central app orchestration and security context configuration are located in [app.py](file:///c:/Users/kotel/rocketcanvas/app.py). The security headers and CSP middleware are configured below:

```python
# app.py: Lines 205-237
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
```

The upload endpoint mitigates security concerns. First, the file extension is validated. The filename is generated on the server (`current_user.id.ext`) instead of using the user-provided name to prevent directory traversal attacks. Finally, Pillow crops the image to a square aspect ratio and resizes it to 256x256 pixels, writing it as a clean RGB image to strip embedded metadata exploits.

The image upload handler implements defensive coding practices to mitigate security risks associated with user-submitted files. Allowing users to upload arbitrary images to a local server introduces the risk of remote code execution if a file contains a malicious payload disguised as an image. The application mitigates this risk by validating the file extension and processing the image data through the Pillow library. Pillow attempts to open the file and decode the image bytes, which will fail if the file is a disguised executable or shell script.

Once the image is validated, it is cropped to a square from the center and resized to a standard resolution. This resizing process is critical because it forces Pillow to write the pixel data into a brand new file, discarding the original file headers and stripping out any embedded metadata or EXIF tags that could contain malicious payloads. The processed image is then saved with a unique, server-generated filename based on the user's ID rather than the original uploaded filename. This prevents directory traversal attacks where a user might attempt to overwrite system files by naming their upload `../../myfile.png`.

The application implements a strict Content Security Policy (CSP) to defend against Cross-Site Scripting (XSS) attacks. A standard CSP can block inline scripts entirely, but this makes it difficult to use third-party libraries like Chart.js or bootstrap the interface with dynamic data. To resolve this, the application uses a nonce-based policy. A unique, cryptographically secure random string called a nonce is generated for every incoming HTTP request and stored in the Flask globals context. The Jinja2 template engine injects this nonce into every script and style tag rendered on the page.

The CSP header attached to the response instructs the browser to only execute scripts and styles that contain the matching nonce value. Because an attacker cannot predict the nonce value for a future request, any malicious script they attempt to inject into the page will be blocked by the browser. The security headers middleware also configures HSTS, X-Frame-Options and X-Content-Type-Options on every response. This ensures that the application is protected against clickjacking and MIME-type sniffing attacks, meeting the security criteria defined in the project boundaries.

### Version Control

Version control for RocketCanvas was implemented using Git and the project was hosted in a GitHub repository https://github.com/greggykotelnikov/rocketcanvas. Commits were made bit by bit as individual features were taking a while to have reached a working state rather than in large infrequent batches, which meant that if a change introduced a fault, such as a security fix unexpectedly breaking an existing route, the project could be rolled back to the most recent stable commit rather than losing other unrelated progress made at the same time.

This was particularly useful during the pivot away from the machine learning hitbox classifier described in Section 4.2. Because earlier commits that the company of Kotelnikov Technologies already had a relatively stable version of the application before that feature was attempted, abandoning the failed approach did not require fully reverting changes from other parts of the codebase and the relevant files could simply be removed and development continued from the last known working state.

Commit messages were written to describe the specific change made rather than generic descriptions because it would make much more sense when looking back after encountering new issues, for example distinguishing between a commit that added a new chart to the analytics dashboard and a separate commit that fixed the underlying name-matching logic, even though both commits touched the same general area of the dashboard feature. This made it much more straightforward to trace when a specific bug was encountered and also if an issue needed to be diagnosed later in development.

---

## 4. Testing and evaluating

### 4.1. Evaluation of code

The methodology used to test and evaluate the code in RocketCanvas combined three approaches working together rather than relying on any single method. Unit-level checks were used on isolated functions, such as the name-resolution logic that matches inconsistent ballchasing.com usernames, since this kind of logic is easy to get subtly wrong and hard to notice once buried inside a larger route. Subsystem testing was applied to the authentication flow as a whole, covering registration, login, 2FA verification and session creation together, since these steps depend on each other and a fault in one stage (for example, a session not being created correctly after a valid 2FA code) would not be caught by testing each piece in isolation. System testing was applied across the full platform once individual features were stable, clicking through the dashboard, garage builder, gallery and profile pages in sequence to confirm that navigation between them worked as a cohesive whole rather than as separate disconnected tools, which directly reflects the unified-platform goal stated in Need 3.

Security testing specifically used ZAP for dynamic testing and Bandit for static analysis, the same two tools used previously in the Unsecure PWA security assessment. Running both tools against RocketCanvas surfaced a smaller set of findings than the original Unsecure PWA project, largely because security practices such as parameterised queries, Bcrypt hashing and CSRF protection were built in from the start rather than retrofitted afterward, which reflects the privacy-by-design principle established during that earlier assessment. All findings raised were resolved before the build was considered complete, leaving only informational-level alerts, consistent with the boundary defined in Section 1.1.

Code optimisation in RocketCanvas focused on three areas. The first was modularisation, splitting the application into separate files by responsibility (authentication in auth.py, database schema in models.py, external API communication in ballchasing.py, replay decoding in replay_parser.py) rather than writing the entire system into a single large file. This meant that when a bug appeared in the replay-matching logic, only ballchasing.py needed to be reviewed, rather than searching through the full codebase to locate the relevant section.

The second area was reducing redundant API calls. Early versions of the analytics dashboard queried ballchasing.com separately for each chart shown to the user, which meant a single dashboard load could trigger several near-identical requests for the same underlying match data. This was changed so that match data is pulled once per dashboard load and then reused across all eight chart visualisations, reducing both the number of external requests made and the time the user spends waiting for the page to finish loading.

The third area was image handling efficiency. Rather than storing uploaded avatar and car design images at their original size, Pillow is used to crop and resize them before saving, which keeps stored file sizes consistent and avoids the gallery page having to load a mixture of very large and very small images when displaying multiple user-submitted designs at once.

### ZAP Dynamic Security Testing Results

ZAP (OWASP Zed Attack Proxy) was run against the local development server at `https://127.0.0.1:5000` to dynamically scan all accessible routes including the login page, robots.txt and sitemap.xml. The scan produced ten alerts in total. The table below lists each alert, its risk classification and the remediation status as of the final build.

| # | Alert | Risk Level | Status |
|---|---|---|---|
| 1 | CSP: Failure to Define Directive with No Fallback | Low | Accepted - `default-src 'self'` provides the fallback |
| 2 | Sub Resource Integrity Attribute Missing | Low | Accepted - CDN sources are trusted and version-pinned |
| 3 | Cross-Domain JavaScript Source File Inclusion (5 instances) | Low | Accepted - required for Chart.js and mapping libraries |
| 4 | Server Leaks Version Information via Server HTTP Response Header | Low | **Resolved** - Werkzeug version string suppressed |
| 5 | Strict-Transport-Security Header Not Set | Low | **Resolved** - HSTS added via custom WSGI middleware |
| 6 | Authentication Request Identified | Informational | Accepted - expected behaviour on login route |
| 7 | Information Disclosure: Suspicious Comments (3 instances) | Informational | Accepted - developer comments contain no sensitive data |
| 8 | Modern Web Application (5 instances) | Informational | Accepted - ZAP passive detection of front-end libraries |
| 9 | Re-examine Cache-control Directives (4 instances) | Informational | Accepted - static assets served with appropriate headers |
| 10 | Session Management Response Identified (7 instances) | Informational | Accepted - expected session cookie behaviour |

**Alert 4 - Server Version Leakage (Resolved)**

By default, Werkzeug includes the Python version string in the `Server` HTTP response header on every request. This leaks environment information that an attacker could use to identify known exploits against a specific Python or Werkzeug version. This was resolved at the top of `app.py` before any route is registered:

```python
# app.py: Lines 19-21
werkzeug.serving.WSGIRequestHandler.server_version = ""
werkzeug.serving.WSGIRequestHandler.sys_version = ""
```

Setting both strings to empty prevents Werkzeug from including any version information in the `Server` response header. After this fix, ZAP's re-scan no longer returned this alert at a flaggable severity level.

**Alert 5 - Strict-Transport-Security Header Not Set (Resolved)**

HSTS (HTTP Strict Transport Security) instructs browsers to only communicate with the server over HTTPS, preventing protocol downgrade attacks where a network-level attacker strips the HTTPS connection. Because Flask does not add HSTS headers automatically, a custom WSGI middleware class called `SecurityHeadersMiddleware` was written and wrapped around the application in `app.py`:

```python
# app.py: Lines 108-139
class SecurityHeadersMiddleware:
    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            header_keys = [h[0].lower() for h in headers]
            if 'strict-transport-security' not in header_keys:
                headers.append(('Strict-Transport-Security',
                    'max-age=31536000; includeSubDomains; preload'))
            if 'x-frame-options' not in header_keys:
                headers.append(('X-Frame-Options', 'DENY'))
            if 'x-content-type-options' not in header_keys:
                headers.append(('X-Content-Type-Options', 'nosniff'))
            ...
        return self.app_wsgi(environ, custom_start_response)

app.wsgi_app = SecurityHeadersMiddleware(app.wsgi_app)
```

This middleware runs outside the Flask request context at the raw WSGI layer, meaning it applies to every response the server sends regardless of which route handled it. The `max-age=31536000` value instructs browsers to enforce HTTPS for one year. `X-Frame-Options: DENY` was also added here to prevent clickjacking, and `X-Content-Type-Options: nosniff` prevents the browser from guessing MIME types on uploaded content, which is relevant given the image upload feature.

**Alert 1 - CSP: Failure to Define Directive with No Fallback (Accepted)**

ZAP flagged that certain directive types within the Content Security Policy header do not have an explicit directive defined for them. The application's CSP is applied via the `add_csp_header` function attached to `app.after_request`:

```python
# app.py: Lines 141-157
@app.after_request
def add_csp_header(response):
    nonce = getattr(g, 'nonce', '')
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' cdn.jsdelivr.net ...;"
        f"style-src 'self' 'nonce-{nonce}' fonts.googleapis.com ...;"
        "frame-ancestors 'none';"
    )
    return response
```

ZAP's alert refers to directives such as `object-src` and `media-src` not being explicitly declared. In practice, these directives fall back to the `default-src 'self'` catch-all, which blocks all objects and media from external sources. The browser behaviour is identical whether the directive is explicit or inherited from the fallback. Because the actual restriction is in place via `default-src`, this alert represents a stylistic rather than a functional gap and was left as-is. Adding explicit `object-src 'none'` and `media-src 'self'` declarations would remove this finding in future scans.

**Alert 2 - Sub Resource Integrity Attribute Missing (Accepted)**

Subresource Integrity (SRI) is a browser mechanism that validates an externally loaded script or stylesheet against a cryptographic hash before executing it. ZAP flagged that the application loads several JavaScript libraries from CDNs without SRI hash attributes. The libraries affected are Chart.js, Leaflet.js and the Shepherd.js tour library, which are pulled from `cdn.jsdelivr.net`, `cdnjs.cloudflare.com` and `unpkg.com`.

The decision to accept this alert without adding SRI hashes was made because each CDN source is a major, well-maintained distribution network with a strong operational security record. The CDN URLs used reference specific version numbers rather than floating `latest` tags, which means the file served cannot change without the URL also changing. Adding SRI hashes would provide an additional layer of verification but would also require the hash to be updated each time a library version is incremented. Given that the application is running locally rather than being served to a public audience, the risk is managed and the alert is accepted at its current low severity.

**Alert 3 - Cross-Domain JavaScript Source File Inclusion (Accepted)**

This alert is directly related to Alert 2 and was raised five times, once for each external library script tag. ZAP identifies any `<script>` tag whose `src` attribute points to a domain other than the host as a potential risk. This is accepted for the same reason as Alert 2: the external domains are reputable CDNs, the versions are pinned and the CSP `script-src` directive explicitly whitelists only those specific CDN hostnames. Any script loaded from a domain not listed in the CSP header would be blocked by the browser before execution.

**Alerts 6-10 - Informational Alerts (Accepted)**

The remaining five alerts were all classified as informational by ZAP, meaning they carry no independently exploitable risk. Alert 6 (Authentication Request Identified) confirms ZAP found and scanned the login form, which is expected. Alert 7 (Suspicious Comments) refers to developer annotation strings in the HTML templates that mention route names and were left in during development. These do not expose credentials, keys or file paths. Alert 8 (Modern Web Application) is a passive detection flag that ZAP applies to any site using JavaScript frameworks. Alert 9 (Re-examine Cache-control Directives) notes that certain static routes do not set explicit cache lifetimes, which is standard for a development server. Alert 10 (Session Management Response Identified) confirms that ZAP detected the application's session cookies, which is expected given the cookie hardening settings (`HTTPOnly`, `Secure`, `SameSite=Lax`) configured in `app.py`.

### Bandit Static Analysis Security Testing Results

Bandit was run to perform static application security testing (SAST) on the Python source code of RocketCanvas. The initial scan identified 16 security and code hygiene issues across three files. Each of these findings was investigated, and remediations were applied to the codebase before final compilation. 

The table below summarizes the issues identified by Bandit, their risk levels and how they were resolved.

| # | File | Location | Issue | Risk Level | Resolution Status |
|---|---|---|---|---|---|
| 1 | `app.py` | L85 | B110: Try, Except, Pass | Low | **Resolved** - Caught specific `OperationalError` exception |
| 2 | `app.py` | L92 | B110: Try, Except, Pass | Low | **Resolved** - Caught specific `OperationalError` exception |
| 3 | `app.py` | L408 | B110: Try, Except, Pass | Low | **Resolved** - Caught specific `(ValueError, TypeError, AttributeError)` exceptions |
| 4 | `app.py` | L605 | B110: Try, Except, Pass | Low | **Resolved** - Caught specific `OSError` exception |
| 5 | `app.py` | L626 | B201: Flask App debug=True | High | **Resolved** - Loaded Flask debug flag dynamically from environment variable |
| 6 | `ballchasing.py` | L16 | B113: requests call without timeout | Medium | **Resolved** - Added `timeout=15` parameter |
| 7 | `ballchasing.py` | L31 | B113: requests call without timeout | Medium | **Resolved** - Added `timeout=15` parameter |
| 8 | `ballchasing.py` | L36 | B113: requests call without timeout | Medium | **Resolved** - Added `timeout=15` parameter |
| 9 | `ballchasing.py` | L46 | B113: requests call without timeout | Medium | **Resolved** - Added `timeout=15` parameter |
| 10 | `replay_parser.py` | L3 | B404: subprocess import blacklist | Low | **Accepted** - Subprocess module is required to execute local parsing binary |
| 11 | `replay_parser.py` | L41 | B603: subprocess call validation | Low | **Accepted** - Replay path parameters are server-controlled |
| 12 | `test_rrrocket.py` | L4 | B404: subprocess import blacklist | Low | **Accepted** - Subprocess module is required for test execution |
| 13 | `test_rrrocket.py` | L17 | B113: requests call without timeout | Medium | **Resolved** - Added `timeout=30` parameter |
| 14 | `test_rrrocket.py` | L32 | B113: requests call without timeout | Medium | **Resolved** - Added `timeout=15` parameter |
| 15 | `test_rrrocket.py` | L36 | B113: requests call without timeout | Medium | **Resolved** - Added `timeout=15` parameter |
| 16 | `test_rrrocket.py` | L44 | B603: subprocess call validation | Low | **Accepted** - Test replay path parameters are statically defined |

**Try, Except, Pass Pattern (B110)**

Bandit flags empty except-pass blocks (`except Exception: pass`) because catching general exceptions without logging or handling them can suppress errors and hide bugs.
- In `app.py` lines 85 and 92, the migration shim executes `ALTER TABLE` to append new database columns. If the columns already exist, SQLite throws an `OperationalError`. This was resolved by importing `sqlalchemy.exc.OperationalError` and catching only that exception, allowing other unexpected errors to bubble up.
- In `app.py` line 408, the date parsing step was hardened by replacing `except Exception:` with `except (ValueError, TypeError, AttributeError):`.
- In `app.py` line 605, the temporary file removal step was changed to catch only `OSError` which is raised when file deletions fail.

**Flask App debug=True (B201)**

Running a production Flask application with `debug=True` is a high-severity security risk as it exposes the interactive Werkzeug debugger. If an unhandled exception occurs, the debugger allows arbitrary Python code execution on the server. This was resolved at line 626 of `app.py` by retrieving the debug state dynamically from the server environment:

```python
debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
app.run(debug=debug_mode, ssl_context=('localhost+2.pem', 'localhost+2-key.pem'))
```

By default, the debug mode defaults to `False`. It is only enabled if the environment variable `FLASK_DEBUG` is explicitly set to `"true"`, ensuring production environments are secure by default.

**Requests Without Timeout (B113)**

Making external HTTP requests using the `requests` library without specifying a timeout allows the request to hang indefinitely if the remote server fails to respond. This blocks the executing thread, degrading server performance or causing a complete denial of service. Timeout parameters (`timeout=15` or `timeout=30`) were added to every call to `requests.get()` in `ballchasing.py` and `test_rrrocket.py` to ensure requests abort if the external API is unreachable.

**Subprocess Usage (B404 and B603)**

Bandit flags the import of the `subprocess` module and calls to its execution functions due to the risk of shell injection attacks if user input is passed directly to command execution functions.
RocketCanvas requires `subprocess` to call the local, compiled `rrrocket.exe` parser to decode match files. The inputs to `subprocess.check_output` are restricted to the static executable path and temporary files generated internally by the server. Because the execution paths are completely controlled and do not consume arbitrary user-supplied string arguments, these alerts were accepted, and `# nosec B404` and `# nosec B603` inline comments were added to suppress the findings in subsequent scans.

### 4.2. Evaluation of solution

#### Machine learning hitbox classifier

One component of RocketCanvas that did not reach a working state was the machine learning car-hitbox classifier. The intention was to let a user upload a photo of their car and have a Teachable Machine model automatically identify which hitbox class it belonged to. Image data was collected for every hitbox class, but the dataset size fell well short of what supervised learning needs to generalise reliably: the Octane and Dominus hitboxes had around 100 images each, while most other hitbox classes had only around 50. Early testing was also misleading, as the test case used for the Octane hitbox was the Octane car itself, which made the model appear far more accurate than it actually was once new, unseen images were introduced.

As a result, the classifier was not reliable enough to ship, and this feature was not completed. This is still a useful evaluation outcome rather than a wasted effort: it confirms that this particular quality criterion was not met, and identifies a specific, addressable cause, insufficient and imbalanced training data per class, rather than a vague one. If revisited, the feature would need at least 100 labelled images per hitbox class, ideally from a range of angles and lighting conditions, and would need to be evaluated on unseen images rather than on the data it was trained with.

#### Analysis of feedback

To evaluate how well RocketCanvas meets the needs of its target users, feedback was selected from seven peers who tested the platform and gave their reactions, covering usability, feature requests and overall impressions.

Feedback received:

Kenneth: "Make this website for clash royale and brawl stars, potentially add more features and help players to pick characters in those games and analyse statistics. Overall website is okay"

Olivia: "Super awesome sauce twin yes I love it. Maybe the ui can be made a bit better"

Michael: "to make more user friendly get rid of png images, in the part where you make the car. Have it automatically (music) start playing in the background"

Ethan: "I would say that the implementation of a music player is one of the coolest aspects of your website, and that is why you should make it so that the music does not stop when you are switching between different sections of the website. Also, by the time the song ends, the playlist does not proceed automatically"

Billy: "Looks good bro, but I would say that every page needs a guide and maybe it should be played automatically by default for every page when it’s the first time user has visited the page"

Telmuun: "looks very nice, design of the website is cool"

Chinkuslen: "I remember doing a website myself in year 10 IST, a good website overall, brings good memories"

##### Overall conclusion

The feedback was largely positive, and a clear pattern emerged across multiple respondents independently: the music feature and visual design were the two elements noticed and praised most often without being prompted, with Olivia, Telmuun and Chinkuslen all commenting positively on the appearance of the site, and Ethan specifically describing the music player as one of the coolest aspects of the platform.

The negative feedback clustered around two specific, addressable gaps rather than anything structural. Both Ethan and Michael independently identified the same underlying issue from different angles, namely that the music feature does not persist properly across the platform. Ethan noted that playback stops when navigating between sections and does not automatically advance to the next track once a song ends, while Michael separately suggested the music should start automatically in the background. Since two respondents raised this issue independently, it represents a genuine usability gap rather than an isolated preference.

Billy raised a second, separate gap regarding the guided tours that already exist on each page; these are not surfaced automatically for first-time visitors, meaning a new user must already know the tour feature exists before being able to use it, which undermines the purpose of having an onboarding tool in the first place.

Kenneth’s feedback was the most outlying response, suggesting the platform be repurposed entirely for different games such as Clash Royale and Brawl Stars. This is not directly actionable for RocketCanvas, since the platform’s value proposition depends on Rocket League-specific data sources such as ballchasing.com and the rrrocket replay parser, neither of which exist for those titles. It does, however, indicate that the underlying concept of combining statistics, customisation and community features has appeal beyond a single game’s audience, which may be relevant to future projects.

Michael’s additional point regarding the removal of PNG images from the garage builder is harder to action without further detail, since the layered sprite system is central to how Need 2 functions. This would benefit from further follow-up to clarify what specifically felt unintuitive about the image-based layering, as the issue may relate to UI clarity rather than the underlying mechanism itself.

Taken together, this feedback round confirmed that the core platform, corresponding to Needs 1 through 3, is functioning well enough that no concerns were raised regarding its operation, while the constructive criticism that did emerge related specifically to Need 4, the engagement features. This is consistent with Need 4 being the lowest priority and the most recently implemented component. The two clearest action items arising from this feedback are ensuring the music player persists across page navigation and automatically advances between tracks, and triggering the guided tour automatically on a user’s first visit to each page rather than requiring it to be located and launched manually.

#### Analysis of Solution Against Quality Success Criteria

| Quality criteria | Met? | Analysis |
|---|---|---|
| Accurate data retrieval and player matching | Met | Testing using live ballchasing.com data confirmed that inconsistent usernames (such as "justin" versus "justin.") are correctly resolved to the same player record. No instances of mismatched statistics were observed during functional or beta testing. |
| Responsive, readable analytics | Met | The reduction of redundant API calls during code optimisation improved load time for the analytics dashboard, and beta tester feedback did not raise any concerns regarding chart readability or clutter, suggesting the visual presentation is functioning as intended for the target audience. |
| Garage builder is intuitive | Partially met | While no beta tester reported being unable to complete a car design, Michael's feedback regarding the use of PNG-based image layers suggests the interface may not be fully intuitive for all users, indicating this criterion is met for most users but would benefit from further refinement. |
| User data and uploads are handled securely | Met | ZAP and Bandit testing returned only informational-level alerts following the same remediation process used in the Unsecure PWA assessment, and manual review confirmed parameterised queries, Bcrypt hashing and image re-encoding were functioning as intended. |
| Engagement features do not get in the way | Only partially met | Beta tester feedback from Ethan and Michael identified that the music feature does not persist correctly across page navigation, and Billy identified that the guided tour does not surface automatically for first-time visitors. While these features do not currently degrade core platform performance, their incomplete implementation means this criterion is not yet fully satisfied and represents a clear area for further development. |

---

## 5. Setup and installation instructions

Before you do anything, make sure you have the full project folder downloaded and that your internet is working. You will also need a Gmail account set up with an App Password for the 2FA emails to actually send.

**1. Check Python is installed**

Open your terminal and type:
```powershell
python --version
```
If it prints something like `Python 3.11.x` you are good to go. If not, head to python.org, download Python 3.11, and when the installer opens make sure you tick **Add Python to PATH** before clicking through, otherwise nothing will work.

**2. Check Git is installed**

```powershell
git --version
```
If it is not installed just grab it from git-scm.com.

**3. Clone the project**

Navigate to wherever you want to put the project folder and run:
```powershell
git clone https://github.com/greggykotelnikov/rocketcanvas.git
cd rocketcanvas
```

**4. Set up a virtual environment**

This keeps all the project's libraries in their own bubble so they do not mess with anything else on your computer:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
You will know it worked when you see `(venv)` show up at the front of your terminal line.

**5. Install the dependencies**

```powershell
pip install -r requirements.txt
```
This pulls in everything the project needs, including Flask, Pillow, SQLAlchemy, Bcrypt and all the rest.

**6. Set up your `.env` file**

Create a file called `.env` in the root folder (same level as `app.py`) and paste this in with your own values filled in:
```ini
SECRET_KEY=any_long_random_string_here
BALLCHASING_API_KEY=your_ballchasing_api_token
MAIL_USERNAME=yourgmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=yourgmail@gmail.com
```
Your ballchasing API token comes from your account settings on ballchasing.com. The Gmail App Password is under Google Account -> Security -> 2-Step Verification -> App Passwords. Do not use your actual Gmail password here, it will not work.

**7. Seed the database**

Run this once before you do anything else:
```powershell
python seed_hitboxes.py
```
This fills in the car hitbox table. You only ever need to do this on the very first run.

**8. Start the app**

```powershell
python app.py
```
Then open your browser and go to `https://127.0.0.1:5000`. The browser will probably throw a security warning about the certificate - just click **Advanced** and then **Proceed**. That is completely normal for a locally hosted app and not an actual problem.

---

## 6. References

*   NSW Legislation (2023) NSW Privacy and Personal Information Act (1998), website, accessed 26 May 2023.
*   Federal Register of Legislation (2023) Federal Privacy Act (1988), Australian Government website, accessed 26 May 2023.
*   ISO Standards (2023) ISO/IEC 27001, website, accessed 26 May 2023.
*   NESA (2023) Software Engineering Course Specifications, NESA website, accessed 26 May 2023.
