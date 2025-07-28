# 🕵️ Detective Buggy: Episode 1 – A Bitter Bite

Detective Inspector Buggy returns to the station... only to find his precious chicken treats have gone missing. Who’s behind the snack sabotage?

This is a lighthearted mystery game built as part of my CS50x final project.

Built using **Python**, **Flask**, **Jinja2**, **Bootstrap**, and **SQLite** — with some (not) very serious paws-on QA 🐶

## 🚀 Features
- 🎤 Interactive suspect interviews
- 🧠 Clue-based deduction system
- 🗣️ Adaptive dialogue based on player progress
- 🗂️ Evidence board & branching logic

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
Some dependencies may not work properly with newer versions (e.g. 3.12+), due to compatibility issues with libraries like Flask or SQLAlchemy.

We recommend using a **virtual environment (`venv`)** to avoid issues across setups.

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

🔗 **Live version:** [https://detective-buggy-ep1.onrender.com](https://detective-buggy-ep1.onrender.com)

## 🛠️ Potential Improvements
A list of potential improvements for future versions:

- ✅ Replace some hardcoded logic with dynamic, database-driven content
- 🧠 Migrate from SQLite to Postgres for data persistence across deploys
- 🗃️ Consider managed DBs like Supabase or Railway
- 📱 Improve layout and styling for mobile and small screens (currently not supported)
- 🎨 Add simple animations for visual polish
- 🎵 Add audio support (ambience, barks, feedback sounds)
- 👣 Track player decisions for enhanced analytics *(note: analytics is currently private and optional)*
- 💾 [Stretch Goal] Implement user login/save progress system — not required for a small game, but a great learning opportunity!

## 👤 Credits

Created by [Jen Skye](https://github.com/skyejen)  
With paw-some assistance from Detective Inspector Buggy 🐶

Special thanks to:
- 🏹 **DCI Longbow** — for character backstories, constant encouragement, and lots of lemon & chili pasta
- 🎓 **CS50x**, my **brother**, and my **engineering crew** — for (re)lighting the spark and proving I could do this after all
