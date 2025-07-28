from flask import Flask, render_template, request, redirect, session, flash, url_for, Response, send_from_directory
from flask_session import Session
import random
from datetime import datetime # This is for playthrough analytics
from dotenv import load_dotenv
import os
import psycopg2 # Added when migrated to PostgreSQL
from urllib.parse import urlparse # Added when migrated to PostgreSQL
from psycopg2.extras import DictCursor


load_dotenv()

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")

    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    conn = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port,
        cursor_factory=DictCursor 
    )
    return conn

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = "super-secret-buggy-code"

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Evidence ID constants
CASE_NOTES_ID = 1                   # Intro notes, added as the beginning of each game
MISSING_BANANA_ID = 2               # A record of Banana not coming for his shift, also added at the beginning of each game
FURBALL_ID = 3                      # Furball at the Crime Scene, main evidence against Cookie
FURBALL_INFO_ID = 4                 # Cookie's explanation for furball being found at the Crime Scene
BIRD_FOOTPRINTS_ID = 5              # Birdlike footprints found at the Crime Scene
CCTV_FOOTAGE_ID = 6                 # CCTV footage from the time of the crime
CHICKEN_ALLERGY_ID = 7              # Spoony's alleged allergy to chicken treats
SPOONY_SUNDAY_SHIFT_ID = 8          # Spoony's claim of working in Records on Sunday
STILTS_ID = 9                       # Stilts with fake bird feet
RUSTY_STAIN_ID = 10                 # Rusty stain on the Security room's closet's handle
PROF_BALLS_COMMENT_ID = 11          # Professor's Ball helpful comment
LOCKER_ROOM_ACCESS_ID = 12          # Unlocks Locker Room acces
SOBBING_BANANA_ID = 13              # Sobbing Banana found in the Security Room's closet
CORRUPTED_CCTV_FOOTAGE_ID = 14      # A record of the CCTV footage being corrupted
LOCKER_TREATS_ID = 15               # Chicken treats found in Spoony's locker
LOCKER_FUR_ID = 16                  # Cookie's fur found in Spoony's locker
BUGGYS_REFLECTIONS = 17             # Buggy's reflection on the case
NOODLE_CLUE_ID = 18                 # Spoony's contradictory alibi

# Flavour (useless) clues
TENNIS_BALL_ID = 19
CHEWED_REPORT_ID = 20
MOTH_ID = 21
MUG_ID = 22
BISCUIT_ID = 23
STICKERS_ID = 24


# Auth stuff for /analytics
def check_auth(username, password):
    expected_username = os.getenv("ANALYTICS_USER")
    expected_password = os.getenv("ANALYTICS_PASSWORD")
    return username == expected_username and password == expected_password

def authenticate():
    return Response(
        'Access denied.\n', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

# PC Noodle bark for multiple routes (helper function)
def maybe_trigger_noodle():
    # Ensure we only do this once
    if session.get("noodle_bark_done"):
        return

    unlocked = session.get("unlocked_evidence", [])

    if (
        session.get("found_banana") and
        RUSTY_STAIN_ID in unlocked and
        STILTS_ID in unlocked and
        PROF_BALLS_COMMENT_ID in unlocked
    ):
        # Mark Noodle bark as triggered
        session["noodle_bark_done"] = True

        # Unlock Noodle's clue
        if NOODLE_CLUE_ID not in unlocked:
            unlocked.append(NOODLE_CLUE_ID)
            flash("🐴 You overhear PC Noodle mumbling: 'I can't believe Records were off on Sunday. Can I ever get a weekend off?'")

        if LOCKER_ROOM_ACCESS_ID not in unlocked:
            unlocked.append(LOCKER_ROOM_ACCESS_ID)
            # flash("🗝️ New location unlocked: Locker Room.")  # Might remove later, don't want it too obvious (?)

        session["unlocked_evidence"] = unlocked
        session.modified = True


# Landing / Title Screen
@app.route("/", methods=["GET", "POST"])
def index():
    session.clear() # Starts a fresh game (default for MVP)
    return render_template("index.html")


# Briefing at the station (story)
@app.route("/briefing")
def briefing():
    session["start_time"] = datetime.now().isoformat() # Timer for the game session for analytics
    return render_template("briefing.html")


# How-To / Tutorial
@app.route("/how-to")
def how_to():
    return render_template("how-to.html")


# Crime Scene
@app.route("/crime-scene", methods=["GET", "POST"])
def crime_scene():

    # Increment visits to the Crime Scene (for when player discoveres the bird prints after CCTV footage corruption)
    session["crime_scene_visits"] = session.get("crime_scene_visits", 0) + 1

    # Create evidence list once, save order in session
    if "crime_scene_evidence_order" not in session:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, label, category, description, image_filename
                FROM evidence
                WHERE LOWER(location) = 'crime scene'
            """)
            raw_evidence = cur.fetchall()
            cur.close()

            raw_evidence = [dict(row) for row in raw_evidence]

        # Later addition of flavour evidence for immersion, this randomises it in the list (once per session)
        important = [e for e in raw_evidence if e["category"] != "flavour"]
        flavour = [e for e in raw_evidence if e["category"] == "flavour"]
        random.shuffle(flavour)

        # Mix in 3 flavour items
        mixed = important[:1] + flavour[:3] + important[1:]
        session["crime_scene_evidence_order"] = [e["id"] for e in mixed]
        session.modified = True

    else:
        # Load based on stored order
        with get_db_connection() as conn:
            cur = conn.cursor()
            mixed = []
            for eid in session["crime_scene_evidence_order"]:
                cur.execute(
                    "SELECT id, name, label, category, description, image_filename FROM evidence WHERE id = %s",
                    (eid,)
                )
                row = cur.fetchone()
                if row:
                    mixed.append(dict(row))
            cur.close()



    # Evidence button logic + flash
    if request.method == "POST":

        # Popup dismissal logic (player clicked on one of the accusation buttons)
        if "popup_dismissed" in request.form:
            session["first_popup_shown"] = True
            session.modified = True
            return redirect("/crime-scene")

        try:
            evidence_id = int(request.form["object"])
        except (ValueError, KeyError):
            flash("❗️Invalid evidence data.")
            return redirect("/crime-scene")

        matching = next((e for e in mixed if e["id"] == evidence_id), None)

        if not matching:
            flash("❗️Unknown evidence.")
            return redirect("/crime-scene")

        # Flavour evidence handling
        if matching["category"] == "flavour":
            unlocked_flavour = session.get("unlocked_flavour", [])
            if evidence_id not in unlocked_flavour:
                unlocked_flavour.append(evidence_id)
                flash(f"🤷 Nothing to see here: {matching['description']}")
                session["unlocked_flavour"] = unlocked_flavour
                session.modified = True
            else:
                flash("📎 You’ve already checked that (still useless).")
            return redirect("/crime-scene")


        # Real evidence
        unlocked = session.get("unlocked_evidence", [])
        if evidence_id not in unlocked:
            unlocked.append(evidence_id)
            flash(f"🧩 New evidence discovered: {matching['name']}.")
        else:
            flash("📌 You’ve already discovered that evidence.")
        session["unlocked_evidence"] = unlocked
        session.modified = True
        return redirect("/crime-scene")

    # Accusation Logic
    unlocked = session.get("unlocked_evidence", [])
    if BIRD_FOOTPRINTS_ID in unlocked and CORRUPTED_CCTV_FOOTAGE_ID in unlocked and not session.get("first_accusation_offered"):
        session["first_accusation_offered"] = True
        session["accusation_stage"] = 1
        session["accusation_origin"] = "crime_scene"
        session["crime_scene_popup_ready"] = True
        session.modified = True

    return render_template("crime-scene.html", evidence=mixed)


# Suspects Board + Professor Ball's Comment Logic
@app.route("/suspects", methods=["GET", "POST"])
def show_suspects():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM suspects")
        suspects = cur.fetchall()
        cur.close()

    final_lock = session.get("final_lock", False)

    progress = session.get("dialogue_progress", {})
    unlocked = session.get("unlocked_evidence", [])

    # Handle Listen button
    show_ball_quote = False
    if request.method == "POST" and "listen_prof_ball" in request.form:

        # Set flag so we don't show Prof Ball again
        session["prof_ball_listened"] = True
        show_ball_quote = True  # Show the quote now
        session.modified = True

        # Unlock evidence if not already unlocked
        if PROF_BALLS_COMMENT_ID not in unlocked:
            unlocked.append(PROF_BALLS_COMMENT_ID)
            session["unlocked_evidence"] = unlocked
            flash("🧩 New evidence discovered: Professor Ball's Comment")

    # Build enhanced suspect list
    enhanced_suspects = []
    for suspect in suspects:
        suspect_dict = dict(suspect)
        suspect_id = str(suspect["id"])

        if suspect["name"] == "DC Banana":
            suspect_dict["alibi_visible"] = True
        else:
            suspect_dict["alibi_visible"] = suspect_id in progress and progress[suspect_id] > 0

        enhanced_suspects.append(suspect_dict)


    # Conditions to show Ball sitting there silently (Listen option)
    show_prof_ball = (
        session.get("found_banana") and
        len(progress) >= 4 and
        not session.get("prof_ball_listened")
    )


    return render_template("suspects.html",
        suspects=enhanced_suspects,
        show_prof_ball=show_prof_ball,
        show_ball_quote=show_ball_quote,
        final_lock=final_lock,
    )


# The Evidence Board (all unlocked evidence so far)
@app.route("/evidence-board", methods=["GET", "POST"])
def evidence_board():

    maybe_trigger_noodle()

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM evidence")
        all_evidence = [dict(row) for row in cur.fetchall()]
        cur.close()

    unlocked = session.get("unlocked_evidence", [])

    # Include evidence that is either unlocked OR always visible
    visible_evidence = [
        ev for ev in all_evidence
        if ev["id"] in unlocked or ev["always_visible"]
    ]

    # Group by category
    clues = [ev for ev in visible_evidence if ev["category"] == "clue"]
    records = [ev for ev in visible_evidence if ev["category"] == "record"]
    notes = [ev for ev in visible_evidence if ev["category"] == "note"]


    return render_template(
        "evidence-board.html",
        clues=clues,
        records=records,
        notes=notes,
        evidence=visible_evidence,  # still needed for {% if evidence %}
        final_lock=session.get("final_lock", False)
    )


# The Interview Lobby / Holding Area (players can select whom to interview)
@app.route("/interview-lobby", methods=["GET", "POST"])
def interview_lobby():

    maybe_trigger_noodle()

    # Get suspects from the database
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM suspects")
        suspects = cur.fetchall()

        # Dialogue counts per suspect (so we know when interviews are complete)
        cur.execute("""
            SELECT suspect_id, COUNT(*) as count
            FROM dialogues
            GROUP BY suspect_id
        """)
        dialogue_counts = cur.fetchall()
        cur.close()

    # Turn dialogue_counts into a dictionary ({ suspect_id: count})
    # This helps us quickly look up how many lines each suspect has
    dialogue_line_count = {}
    for row in dialogue_counts:
        suspect_id = row["suspect_id"]
        number_of_lines = row["count"]
        dialogue_line_count[suspect_id] = number_of_lines

    # Initialise session keys if missing
    if "dialogue_progress" not in session:
        session["dialogue_progress"] = {}

    if "interviewed_suspects" not in session:
        session["interviewed_suspects"] = []

    # Grab session data
    progress = session["dialogue_progress"]
    interviewed_suspects = session["interviewed_suspects"]

    # Attach a 'status' label to each suspect based on progress
    mutable_suspects = [] # had to do it this way as was hitting 500 due to trying to change SQL row object

    for row in suspects:
        suspect = dict(row)  # Convert to a mutable dict

        suspect_id = suspect["id"]
        suspect_id_str = str(suspect_id)

        total_lines = dialogue_line_count.get(suspect_id, 0)
        current_index = progress.get(suspect_id_str, 0)

        if current_index == 0:
            suspect["status"] = "Not started"
        elif current_index < total_lines:
            suspect["status"] = "In progress"
        else:
            suspect["status"] = "Complete"

        # Banana logic
        if suspect["name"] == "DC Banana":
            if not session.get("found_banana"):
                suspect["disabled"] = True
                suspect["status"] = "Missing"
                suspect["status_message"] = "Interview (Unavailable)"
            else:
                # Banana has been found —> allow interview
                suspect["status"] = "Not started" if current_index == 0 else (
                    "In progress" if current_index < total_lines else "Complete"
                )
                suspect["status_message"] = "Interview"

        mutable_suspects.append(suspect)

    # Sort by status, then alphabetically
    # Define priority mapping
    status_priority = {
        "In progress": 1,
        "Not started": 2,
        "Complete": 3
    }

    # Helper to sort suspects
    def sort_suspects(suspect):
        status = suspect["status"]
        name = suspect["name"]
        return (status_priority.get(status, 99), name.lower())

    # Apply sorting to the mutable list
    mutable_suspects.sort(key=sort_suspects)

    # Debug text to check for Banana flag
    print("Banana found:", session.get("found_banana"))


    # Show the lobby with all suspect statuses
    return render_template(
        "interview-lobby.html",
        suspects=mutable_suspects,
        interviewed=interviewed_suspects
    )


# The Interview Room (the actual dialogue with the suspects)
@app.route("/interview-lobby/<int:suspect_id>", methods=["GET", "POST"])
def interview_suspect(suspect_id):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM suspects WHERE id = %s", (suspect_id,))
        suspect = cur.fetchone()

        cur.execute("SELECT * FROM dialogues WHERE suspect_id = %s", (suspect_id,))
        dialogue_lines = cur.fetchall()

        # Pre-fetch evidence for fast access
        cur.execute("SELECT id, name FROM evidence")
        evidence_lookup = cur.fetchall()
        cur.close()

    if not suspect:
        return "Suspect not found", 404

    # Initialise session storage if missing
    if "interviewed_suspects" not in session:
        session["interviewed_suspects"] = []

    if "unlocked_evidence" not in session:
        session["unlocked_evidence"] = []

    if "dialogue_progress" not in session:
        session["dialogue_progress"] = {}

    # For template rendering
    show_log = False  # Default fallback to avoid UnboundLocalError

    # Mark this suspect as interviewed
    if suspect_id not in session["interviewed_suspects"]:
        session["interviewed_suspects"].append(suspect_id)

    # Get this suspect's current dialogue index
    progress = session["dialogue_progress"]
    current_index = progress.get(str(suspect_id), 0) # Converting to str cause it's stored in JSON which only allows strs

    # Turn evidence_lookup values into a dictionary for easy access (for evidence_name below)
    evidence_map = {}
    for row in evidence_lookup:
        evidence_id = row["id"]
        evidence_name = row["name"]
        evidence_map[evidence_id] = evidence_name

    # Fetch the current dialogue line
    current_line = None
    if current_index < len(dialogue_lines):
        current_line = dialogue_lines[current_index]

        # Unlock evidence if linked
        evidence_id = current_line["evidence_id"]
        if evidence_id and evidence_id not in session["unlocked_evidence"]:
            session["unlocked_evidence"].append(evidence_id)

            # Fetch evidence name based on the dictionary created above (if doesn't exist, display "Unknown Evidence")
            if evidence_id in evidence_map:
                evidence_name = evidence_map[evidence_id]
            else:
                evidence_name = "Unknown Evidence"

            flash(f"🧩 New evidence discovered: {evidence_name}")

    # Advance dialogue on POST (MUST go first to avoid show_log error)
    if request.method == "POST":
        progress[str(suspect_id)] = current_index + 1 # Converting to str cause it's stored in JSON which only allows strs
        session["dialogue_progress"] = progress
        session.modified = True
        return redirect(url_for("interview_suspect", suspect_id=suspect_id))

    # Fetch the current line or prepare log
    interview_complete = current_index >= len(dialogue_lines)

    # Flag to show log instead of "Continue" (for the read-only interview logs)
    if interview_complete:
        current_line = None  # No active line left to show (So HTML won’t try to show another line)
        show_log = True
    else:
        current_line = dialogue_lines[current_index]
        show_log = False

    return render_template(
        "interview-suspect.html",
        suspect=suspect,
        current_line=current_line,
        show_log=show_log, # Needed for log replay
        dialogue_lines=dialogue_lines,
    )


# Security room
@app.route("/security-room", methods=["GET", "POST"])
def security_room():
    # Init session flags
    session.setdefault("unlocked_evidence", [])
    session.setdefault("seen_room", False)
    session.setdefault("found_banana", False)
    session.setdefault("first_accusation_offered", False)
    session.setdefault("steven_denial_shown", False)
    session.setdefault("accusation_origin", None)
    session.setdefault("heard_banana", False)  # New flag for Banana trigger

    # Unpack key states
    unlocked = CCTV_FOOTAGE_ID in session["unlocked_evidence"]
    corrupted_unlocked = CORRUPTED_CCTV_FOOTAGE_ID in session["unlocked_evidence"]
    birdprints_found = BIRD_FOOTPRINTS_ID in session["unlocked_evidence"]
    found_banana = session["found_banana"]

    # Mark first time visit
    if not session["seen_room"]:
        session["seen_room"] = True
        session.modified = True

    # Logic for playing the CCTV footage
    if request.method == "POST" and unlocked and not corrupted_unlocked:
        session["unlocked_evidence"].append(CORRUPTED_CCTV_FOOTAGE_ID)
        session["seen_security_room"] = True
        session["steven_denial_shown"] = True
        session["just_played_cctv"] = True  # Only for next GET

        # Show accusation pop-up if bird prints already found
        if birdprints_found and not session["first_accusation_offered"]:
            session["first_accusation_offered"] = True
            session["accusation_stage"] = 1
            session["accusation_origin"] = "security"

        flash("🧩 New evidence discovered: Corrupted CCTV Footage.")
        session.modified = True
        return redirect(url_for("security_room"))

    # For the "Keep Investigating" button to mark the accusation pop-up as rejected and refresh the Security Room and trigger Banana sequence
    if request.method == "POST":

        # Popup dismissal logic (player clicked on one of the accusation buttons)
        if "popup_dismissed" in request.form:
            session["first_popup_shown"] = True
            session.modified = True

        choice = request.form.get("choice")
        if choice == "security-room":
            return redirect(url_for("security_room"))
        elif choice == "evidence-board":
            return redirect(url_for("evidence_board"))

    # Post-footage revisit: trigger Banana sequence if ready
    if (
        session.get("seen_security_room")
        and corrupted_unlocked
        and birdprints_found
        and not found_banana
        and not session.get("heard_banana")
    ):
        session["heard_banana"] = True
        session.modified = True

    # Render page
    return render_template(
        "security-room.html",
        unlocked=unlocked,
        corrupted_unlocked=corrupted_unlocked,
        found_banana=found_banana,
        birdprints_found=birdprints_found,
    )


# Security closet (continuation of the security room storyline + Banana)
@app.route("/security-closet", methods=["GET", "POST"])
def security_closet():

    # Initialise session memory
    session.setdefault("closet_progress", 0)
    session.setdefault("unlocked_evidence", [])
    session.setdefault("unlocked_flavour", [])
    session.setdefault("found_banana", False)
    session.setdefault("closet_looked_around", False)
    session.setdefault("declined_accusation", False)

    # Reset if just declined accusation
    if session["declined_accusation"]:
        session["closet_progress"] = 0
        session["closet_looked_around"] = False
        session["declined_accusation"] = False
        session.modified = True

    progress = session["closet_progress"]

    # Narrattion lines (trying a different way for learning, previously all content was in HTMLs)
    closet_lines = [
        "You open the supply closet and carefully look inside...",
        "Inside, you find DC Banana curled up, sobbing quietly. They flinch as you enter.",
        "This officer seems traumatised. They might need a moment..."
    ]

    last_index = len(closet_lines) - 1
    if progress > last_index:
        progress = last_index

    current_line = closet_lines[progress]
    show_continue = progress < last_index
    show_look_button = not show_continue and not session["closet_looked_around"]
    show_evidence = session["closet_looked_around"]
    line_index = progress


    evidence_list = []
    if show_evidence:
        if "closet_evidence_order" not in session:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, name, label, category, description
                    FROM evidence
                    WHERE origin = %s AND (category = 'clue' OR category = 'flavour')
                """, ("Security Room Closet",))
                raw_evidence = cur.fetchall()
                cur.close()

            important = [e for e in raw_evidence if e["category"] != "flavour"]
            flavour = [e for e in raw_evidence if e["category"] == "flavour"]
            random.shuffle(flavour)

            # Insert up to 3 flavour items
            mixed = important[:1] + flavour[:2] + important[1:] + flavour[2:]

            session["closet_evidence_order"] = [e["id"] for e in mixed]
            session.modified = True
        else:
            with get_db_connection() as conn:
                cur = conn.cursor()
                mixed = []
                for eid in session["closet_evidence_order"]:
                    cur.execute("""
                        SELECT id, name, label, category, description
                        FROM evidence
                        WHERE id = %s
                    """, (eid,))
                    row = cur.fetchone()
                    if row:
                        mixed.append(row)
                cur.close()
        evidence_list = mixed


    # Handle interactions
    if request.method == "POST":
        if "object" in request.form:
            evidence_name = request.form["object"]
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, name, category, description FROM evidence WHERE name = %s",
                    (evidence_name,)
                )
                evidence = cur.fetchone()
                cur.close()

            if evidence:
                if evidence["category"] == "flavour":
                    if evidence["id"] not in session["unlocked_flavour"]:
                        session["unlocked_flavour"].append(evidence["id"])
                        flash(f"🤷 Nothing to see here: {evidence['description']}")
                        session.modified = True
                    else:
                        flash("📎 You’ve already checked that (still useless).")
                else:
                    if evidence["id"] not in session["unlocked_evidence"]:
                        session["unlocked_evidence"].append(evidence["id"])
                        flash(f"🧩 New evidence discovered: {evidence['name']}.")
                        session.modified = True
            return redirect(url_for("security_closet"))

        elif "look" in request.form:
            session["closet_looked_around"] = True
            session.modified = True
            return redirect(url_for("security_closet"))

        else:
            session["closet_progress"] += 1
            progress = session["closet_progress"]
            session.modified = True

            # Unlock Banana clue
            if progress == 1:
                if SOBBING_BANANA_ID not in session["unlocked_evidence"]:
                    session["unlocked_evidence"].append(SOBBING_BANANA_ID)
                    session["found_banana"] = True
                    flash(f"🧩 New evidence discovered: Sobbing Banana.")
                    session.modified = True

            return redirect(url_for("security_closet"))

    return render_template("security-closet.html",
        current_line=current_line,
        show_continue=show_continue,
        show_look_button=show_look_button,
        show_evidence=show_evidence,
        evidence_list=evidence_list,
        line_index = line_index,
    )


# Reporting Screen (the player will attempt to accuse one of the suspects to win the game)
@app.route("/accuse", methods=["GET", "POST"])
def accuse():
    # Allow if accusation is unlocked
    can_accuse = session.get("first_accusation_offered", False)

    if not can_accuse:
        return render_template("accuse.html", not_ready=True)
    
    if session.get("accusation_submitted"):
        flash("🚫 You've already made an accusation. No take-backsies! 🐶 Buggy is watching...")
        return render_template("accuse_closed.html")

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM suspects")
        suspects = cur.fetchall()
        cur.close()

    if request.method == "POST":
        accused_name = request.form.get("accused")
        if accused_name:
            session["accused_name"] = accused_name
            session["accusation_submitted"] = True
            session.modified = True
            return redirect(url_for("verdict"))

    return render_template("accuse.html", not_ready=False, suspects=suspects)


# Helper page so cheeky players (like my bf) don't go back to change whom they previously wrongly accused
@app.route("/accuse-closed")
def accuse_closed():
    flash("🚫 You've already made an accusation. No take-backsies!")
    return render_template("accuse_closed.html")


# Locker Room - the final locaton before the end of the game
@app.route("/locker-room", methods=["GET", "POST"])
def locker_room():
    session.setdefault("locker_progress", 0)
    session.setdefault("unlocked_evidence", [])
    session.setdefault("final_lock", False)

    lines = [
        "You burst into the Locker Room and catch DS Spoony red-handed, his locker wide open... a look of panic flashes across his face.",
        "Inside the locker, you spot a stash of chicken treats.",
        "A few tufts of fur cling to the locker door — unmistakably from DS Cookie.",
        "DS Spoony sputters: 'It’s not what it looks like! Cookie’s been trying to frame me!'",
        "📝 Buggy takes a moment to reflect. Maybe the Evidence Board will help piece it all together before the final decision..."
    ]

    idx = min(session["locker_progress"], len(lines) - 1)
    if idx >= len(lines):
        idx = len(lines) - 1

    current_line = lines[idx]
    show_continue = idx < len(lines) - 1
    line_index = idx

    if request.method == "POST":
        session["locker_progress"] += 1
        idx = session["locker_progress"]
        unlocked = session["unlocked_evidence"]

        if idx == 1:
            # Chicken treats
            if LOCKER_TREATS_ID not in unlocked:
                unlocked.append(LOCKER_TREATS_ID)
                flash("🧩 New evidence discovered: Chicken Treats in Spoony's Locker")

        if idx == 2:
            # Cookie’s Fur
            if LOCKER_FUR_ID not in unlocked:
                unlocked.append(LOCKER_FUR_ID)
                flash("🧩 New evidence discovered: Cookie's Fur in Spoony's Locker")

        if idx == 4:
            # Buggy's thoughts
            if BUGGYS_REFLECTIONS not in unlocked:
                unlocked.append(BUGGYS_REFLECTIONS)
                flash("🧩 New evidence discovered: Buggy's Reflections")
            session["final_lock"] = True  # Flag to lock down nav on board

        session["unlocked_evidence"] = unlocked
        session.modified = True
        return redirect(url_for("locker_room"))

    return render_template("locker-room.html",
                           current_line=current_line,
                           line_index = line_index,
                           show_continue=show_continue)


# The Verdict Screen (the end game screen either winning if accusation is correct, or losing if not)
@app.route("/verdict")
def verdict():

    # Block direct access unless an accusation was made
    accused = session.get("accused_name")
    if not accused:
        flash("You can’t reach the verdict without making an accusation!")
        return redirect(url_for("evidence_board"))

    # Get guilty suspect from DB
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM suspects WHERE is_guilty = TRUE")
        guilty_row = cur.fetchone()
        cur.close()

    guilty_name = guilty_row["name"] if guilty_row else None

    # Compare accused vs actual guilty
    win = (accused == guilty_name)

    return render_template(
        "verdict.html",
        accused=accused,
        guilty=guilty_name,
        win=win
    )


# The Archives route (signing logs and viewing investigation info)
@app.route("/archives")
def archives():

    # Make sure player can’t just visit /verdict directly
    accused = session.get("accused_name")

    # Calculate duration
    start_time = session.get("start_time")
    end_time = datetime.now()
    duration_minutes = None

    if start_time:
        start_dt = datetime.fromisoformat(start_time)
        duration_minutes = round((end_time - start_dt).total_seconds() / 60)

    if not accused:
        flash("You can't come to the Archives without making an accusation!")
        return redirect(url_for("evidence_board"))

    # Get guilty suspect from DB
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM suspects WHERE is_guilty = TRUE")
        guilty_row = cur.fetchone()
        cur.close()

    guilty_name = guilty_row["name"] if guilty_row else None

    # Compare accused vs actual guilty
    win = (accused == guilty_name)

    player_name = session.get("player_name", "")

    # Log playthrough (only once per session)
    if "playthrough_id" not in session:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO playthroughs (timestamp, player_name, accused_name, was_correct, duration_minutes)
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """, (
                end_time.isoformat(),
                player_name,
                accused,
                win,
                duration_minutes
            ))
            session["playthrough_id"] = cur.fetchone()["id"]
            session.modified = True
            cur.close()

    # Clean up session
    session["endgame_reached"] = True
    session.modified = True

    return render_template(
        "archives.html",
        accused=accused,
        guilty=guilty_name,
        win=win,
        duration_minutes=duration_minutes,
        player_name=player_name,
        logs_signed=session.get("logs_signed", False)
    )

@app.route("/submit_name", methods=["POST"]) # Just an endpoint to handle name submission
def submit_name():

    # Add a name to the playthrough log (if name is provided)
    submitted_name = request.form.get("player_name", "").strip()
    if submitted_name and "playthrough_id" in session:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE playthroughs
                SET player_name = %s
                WHERE id = %s
            """, (submitted_name, session["playthrough_id"]))
            cur.close()
        session["player_name"] = submitted_name
        session["logs_signed"] = True
        session.modified = True

    # Not popping playthrough_id here because session.clear() will handle it on restart

    return redirect(url_for("archives"))

# Credits & Behind the Scenes
@app.route("/credits")
def credits():

    cast = [
        {
            "name": "DI Buggy",
            "front_img": "img/scenes/buggy-title-screen.webp",
            "back_img": "img/credits/buggy-real.webp",
            "pos_front": "60% 10%",
            "pos_back": "center"
        },
        {
            "name": "DS Cookie",
            "front_img": "img/suspects/cookie.webp",
            "back_img": "img/credits/cookie-real.webp",
            "pos_front": "40% 30%",
            "pos_back": "40% 90%",
        },
        {
            "name": "DS Theo",
            "front_img": "img/suspects/theo.webp",
            "back_img": "img/credits/theo-real.webp",
            "pos_front": "40% 15%",
            "pos_back": "40% 65%",
        },
        {
            "name": "PC Noodle",
            "front_img": "img/suspects/noodle.webp",
            "back_img": "img/credits/noodle-real.webp",
            "pos_front": "40% 15%",
            "pos_back": "center"
        },
        {
            "name": "DS Steven",
            "front_img": "img/suspects/steven.webp",
            "back_img": "img/credits/steven-real.webp",
            "pos_front": "40% 25%",
            "pos_back": "center"
        },
        {
            "name": "DC Banana",
            "front_img": "img/suspects/banana.webp",
            "back_img": "img/credits/banana-real.webp",
            "pos_front": "40% 67%",
            "pos_back": "40% 25%",
        },
        {
            "name": "DS Spoony",
            "front_img": "img/suspects/spoony.webp",
            "back_img": "img/credits/spoony-real.webp",
            "pos_front": "40% 27%",
            "pos_back": "40% 25%",
        },
        {
            "name": "Professor Ball",
            "front_img": "img/scenes/professor-ball.webp",
            "back_img": "img/credits/professor-ball-real.webp",
            "pos_front": "15% 10%",
            "pos_back": "15% 50%",
        },
    ]

    return render_template("credits.html", cast=cast)


# Helps locate favicon in other folders (and removes the annoying 404...)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'img', 'ui'),
        'favicon.png',
        mimetype='image/png'
    )


# Internal only
@app.route("/analytics")
def analytics():

    # Auth to protect analytics
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM playthroughs ORDER BY timestamp DESC")
        playthroughs = cur.fetchall()
        cur.close()

        total = len(playthroughs)

        # Start with zero correct guesses
        correct = 0

        # Go through each playthrough
        for row in playthroughs:

            # If the "was_correct" column is 1 (i.e. correct)
            if row["was_correct"]:
                correct += 1

        # Make an empty list to hold all durations
        durations = []

        # Go through each playthrough
        for row in playthroughs:

            # Skip if there's no duration
            if row["duration_minutes"] is None:
                continue

            # If duration is 0, round up to 1
            clean_duration = max(1, row["duration_minutes"] or 0)

            # Add it to the list
            durations.append(clean_duration)

        # Calculate average (if we have at least one duration)
        if durations:
            avg_duration = round(sum(durations) / len(durations), 1)
        else:
            avg_duration = 0

        stats = {
            "total": total,
            "correct": correct,
            "correct_pct": round((correct / total) * 100, 1) if total > 0 else 0,
            "avg_duration": avg_duration
        }

    return render_template("analytics.html", playthroughs=playthroughs, stats=stats)


# To force browser to check accuse route when using the broswer back button
@app.after_request
def add_no_cache_headers(response):

    # Don't add no-cache headers to static files
    if not request.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# Locking the game after reaching verdict
@app.before_request
def prevent_post_verdict_backtracking():
    print(f"Checking route guard for {request.path}")
    
    # Use tuple for faster `startswith` matching
    safe_prefixes = ("/", "/verdict", "/archives", "/static")
    
    # Check if player already submitted their final accusation
    if session.get("accusation_submitted"):
        
        # If the current path isn't one of the allowed prefixes, block it
        if not request.path.startswith(safe_prefixes):
            flash("🔒 Buggy says the case is closed. No snooping around the past!")
            return redirect(url_for("verdict"))


if __name__ == "__main__":
    app.run(debug=True)
