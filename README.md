# 🕵️ Detective Buggy: A Bitter Bite (Episode 1)

Detective Inspector Buggy returns to the station... only to find his precious chicken treats have gone missing. Who’s behind the snack sabotage?

This is a lighthearted mystery game built as part of my CS50x final project (see the [CS50x Assignment Submission Info](#-cs50x-assignment-submission-info) section below)

It was also my first deployed Flask project, and it taught me a ton: managing scope, balancing logic with storytelling, handling real user input, creating routes and endpoints, and passing information between backend and frontend. I got much more comfortable with Git and GitHub, learned how to deploy with Render, and worked with databases — starting with SQLite and later migrating to PostgreSQL

There’s definitely room for improvement (session handling, conditional logic in Jinja, some DB queries could be cleaner and more — see the [Potential Improvements](#%EF%B8%8F-potential-improvements) section below), but I’m proud of how much I learned — and deeply grateful for the support I had to finish it. It was terrifying at first, but I did it 🧠✨

Built using **Python**, **Flask**, **Jinja2**, **Bootstrap**, and **PostgreSQL** — with some (not very serious) paws-on QA 🐶

🔗 **Live version:** [https://detective-buggy-ep1.onrender.com](https://detective-buggy-ep1.onrender.com)
<br><sub><em>💡**Note:** This app is hosted on Render’s free tier, so it may take a minute or two to load the first time.</em></sub>

## 🪄 CS50x Assignment Submission Info

<details>
<summary>👉 Click to expand details</summary>

### 📝 Submission Details

- 👤 **Author Info:** Available at the in-app route [`/cs50-info`](https://detective-buggy-ep1.onrender.com/cs50-info)
- 🎥 **Video Demo:** [CS50x Final Project Walkthrough](https://youtu.be/pxXjlVCa3zw)

### 🧪 Tech Stack

This project is built with a Flask-based backend and uses server-side rendering to deliver a dynamic, story-driven experience. It relies on session-based logic and a database of clues, suspects, and player decisions.

- **Flask:** Web framework used to manage routes, templates, and sessions
- **Jinja2:** Templating engine for dynamic HTML rendering
- **PostgreSQL:** Backend database for storing suspects, dialogue, evidence, and player analytics
- **psycopg2 (with pooling):** Direct database access via PostgreSQL driver, using `SimpleConnectionPool` for efficient connection reuse
- **Bootstrap 5:** CSS framework used for responsive layout and UI components
- **Custom CSS:** Themed design built with dark mode, custom fonts, and animation-friendly layout
- **Render:** Hosting provider used for both app and PostgreSQL deployment, with auto-updates on GitHub pushes

### 📁 Project File Structure

```bash
.
├── app.py                     # Main Flask app with all route logic and game state
├── templates/                 # Jinja2 HTML templates
│   ├── layout.html            # Shared layout
│   ├── *.html                 # All views (crime scene, interviews, etc.)
├── static/                    # Static assets
│   ├── img/                   # Images (evidence, suspects, UI)
│   ├── styles.css             # Custom theme & responsive styling
│   └── js/scripts.js          # JS for pop-ups and interactivity
├── schema.sql                 # PostgreSQL schema (suspects, evidence, dialogues, etc.)
├── requirements.txt           # Dependencies list
├── .env.example               # Environment variable placeholders
└── README.md                  # Project documentation
```

## 🔍 Internal Tools

This project also features a private `/analytics` dashboard (protected by HTTP Basic Auth), used to view:
- Number of total playthroughs
- Average playtime
- Percentage of correct accusations

This was not required for CS50x but was added as a personal learning extension (and because I'm nosey).

## 🤖 AI Assistance
Parts of this project were influenced or assisted by AI (ChatGPT), particularly for Flask routing logic, debugging help, and code structure advice — as well as for all artwork. I also used it extensively during the migration from SQLite to PostgreSQL. Final implementation, logic, and design decisions are my own.

</details>

## 🚀 Features
- 🎤 **Interactive suspect interviews** — Each character has a unique personality, backstory, and dialogue path
- 🧠 **Clue-based deduction system** — Players must unlock, track, and interpret clues to solve the case
- 🗣️ **Adaptive dialogue & progression** — Interviews and locations evolve based on your investigation choices
- 🗂️ **Dynamic evidence board** — Clues and records update in real time as you uncover new leads
- 🕵️‍♀️ **Player-driven investigation** — Accusation options appear dynamically based on your progress and decisions
- 🎨 **Custom dark-mode UI** — Built with Bootstrap, themed CSS, and playful interactions
- 🧾 **[Private] in-game analytics** — View player stats, accuracy, and average playtime via a private dashboard

## 🎨 Art & Assets

All character and background illustrations were generated with the help of ChatGPT's image generation tool, based on descriptions of real pets and my doggo's toys.

No external art was used, and all styling/UI was designed specifically for this project.

## 🖼️ Screenshots

<details>
<summary>👉 Click to expand screenshots</summary>

### Title Screen
<img src="screenshots/title-screen.png" width="800"/>

### Briefing Screen
<img src="screenshots/briefing-screen.png" width="800"/>

### Suspect Board
<img src="screenshots/suspect-board.png" width="800"/>

</details>

## 🛠️ Run Locally

Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
flask run
```

💡 If flask run doesn’t work, try setting ```FLASK_APP=app.py``` or running ```python app.py``` directly.

Ensure python-dotenv is installed and a .env file exists for your secret keys (if applicable).

### ⚠️ Recommended Python Version

**Python 3.10.x is recommended**  
Some dependencies may not work properly with newer versions (e.g. 3.12+), due to compatibility issues with Flask sessions.

**Note:** requirements.txt is a minimal dependency list. See requirements-locked.txt for full frozen environment.

We (Buggy and I!) recommend using a **virtual environment (`venv`)** to avoid issues across setups.

<details>
<summary>Set up a virtual environment</summary>

```bash
# Make sure Python 3.10 is installed
python3.10 -m venv venv

# Activate it:
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt
```
</details>

## 🌐 Hosting
This project is deployed using Render.
Deployment instructions or render.yaml will be added in a future update.

## 🛠️ Potential Improvements
A list of potential improvements for future versions:

- ✅ Replace some hardcoded logic with dynamic, database-driven content
- 🛡️ Migrate from psycopg2 to SQLAlchemy for maintainability and async potential
- 🎨 Add simple animations for visual polish
- 🎵 Add audio support (ambience, barks, feedback sounds)
- 👣 Track player decisions for enhanced analytics *(note: analytics is currently private and optional)*
- 🪄 Fix line-breaks (yes, 8 years in localisation?.. good line-breaks is life!)
- 🧪 Lacks automated tests — unit testing DB/session logic is a future (fun) goal
- 💾 [Stretch Goal] Implement user login/save progress system — not required for a small game, but a great learning opportunity!

**Note:** Free-tier Postgres on Render expires every 90 days (next: end of August). May consider upgrading or migrating later.

## 👤 Credits

Created by [Jen Skye](https://github.com/skyejen)  
With paw-some assistance from Detective Inspector Buggy 🐶

Special thanks to:
- 🏹 **DCI Longbow** — for character backstories, constant encouragement, and lots of lemon & chili pasta
- 🎓 **CS50x**, my **brother**, and my **engineering crew** — for (re)lighting the spark and proving I could do this after all
