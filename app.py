from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import date
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)



# ==========================================
# FLASK SECRET KEY
# ==========================================


app.secret_key = os.getenv("SECRET_KEY")

# ==========================================
# SQLITE DATABASE
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "diary.db")


# ==========================================
# PRETTY DATE FILTER
# ==========================================

@app.template_filter("prettydate")
def prettydate(value):

    if not value:
        return ""

    try:
        return value.strftime("%B %d, %Y")

    except (AttributeError, ValueError):

        try:
            return date.fromisoformat(str(value)).strftime("%B %d, %Y")
        except ValueError:
            return str(value)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    # Makes database rows behave like dictionaries.
    # Example:
    # entry["title"]
    # entry["entry_id"]
    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_database():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS diary_entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_date DATE NOT NULL,
            title TEXT NOT NULL,
            mood TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()

    cursor.close()
    connection.close()


# Create the SQLite database/tables automatically
# when the application starts.
init_database()


# ==========================================
# LOGIN REQUIRED
# ==========================================

def login_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please log in first.",
                "error"
            )

            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated


# ==========================================
# LANDING PAGE
# ==========================================

@app.route("/")
def index():

    return render_template("landing.html")


# ==========================================
# REGISTER
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        if not username or not password or not confirm_password:

            flash(
                "Please fill in all fields.",
                "error"
            )

            return redirect(url_for("register"))


        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(url_for("register"))


        connection = get_db_connection()

        cursor = connection.cursor()

        try:

            # Check if username already exists
            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE username = ?
                """,
                (username,)
            )

            existing_user = cursor.fetchone()


            if existing_user:

                flash(
                    "Username already exists.",
                    "error"
                )

                return redirect(url_for("register"))


            # Hash password
            hashed_password = generate_password_hash(
                password
            )


            # Insert new user
            cursor.execute(
                """
                INSERT INTO users
                (
                    username,
                    password
                )
                VALUES (?, ?)
                """,
                (
                    username,
                    hashed_password
                )
            )


            connection.commit()


            flash(
                "Registration successful. You can now log in.",
                "success"
            )

            return redirect(url_for("login"))


        except sqlite3.Error as e:

            connection.rollback()

            print(
                "Registration error:",
                e
            )

            flash(
                "Something went wrong during registration.",
                "error"
            )

            return redirect(url_for("register"))


        finally:

            cursor.close()
            connection.close()


    return render_template("register.html")


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        if not username or not password:

            flash(
                "Please enter your username and password.",
                "error"
            )

            return redirect(url_for("login"))


        connection = get_db_connection()

        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    user_id,
                    username,
                    password
                FROM users
                WHERE username = ?
                """,
                (username,)
            )

            user = cursor.fetchone()


            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["user_id"]
                session["username"] = user["username"]

                return redirect(
                    url_for("dashboard")
                )


            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(url_for("login"))


        except sqlite3.Error as e:

            print(
                "Login error:",
                e
            )

            flash(
                "Something went wrong during login.",
                "error"
            )

            return redirect(url_for("login"))


        finally:

            cursor.close()
            connection.close()


    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
@login_required
def dashboard():

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        user_id = session["user_id"]


        # ----------------------------------
        # RECENT ENTRIES
        # ----------------------------------

        cursor.execute(
            """
            SELECT
                entry_id,
                entry_date,
                title,
                mood,
                content
            FROM diary_entries
            WHERE user_id = ?
            ORDER BY entry_date DESC, entry_id DESC
            LIMIT 5
            """,
            (user_id,)
        )

        recent_entries = cursor.fetchall()


        # ----------------------------------
        # TOTAL ENTRIES
        # ----------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total_entries
            FROM diary_entries
            WHERE user_id = ?
            """,
            (user_id,)
        )

        total_entries = cursor.fetchone()["total_entries"]


        # ----------------------------------
        # ENTRIES THIS MONTH
        # ----------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS month_entries
            FROM diary_entries
            WHERE user_id = ?
            AND strftime('%m', entry_date) = strftime('%m', 'now')
            AND strftime('%Y', entry_date) = strftime('%Y', 'now')
            """,
            (user_id,)
        )

        month_entries = cursor.fetchone()["month_entries"]


        # ----------------------------------
        # MOST COMMON MOOD
        # ----------------------------------

        cursor.execute(
            """
            SELECT
                mood,
                COUNT(*) AS mood_count
            FROM diary_entries
            WHERE user_id = ?
            GROUP BY mood
            ORDER BY mood_count DESC
            LIMIT 1
            """,
            (user_id,)
        )

        mood_result = cursor.fetchone()


        if mood_result:

            most_common_mood = mood_result["mood"]

        else:

            most_common_mood = "—"


        return render_template(
            "dashboard.html",
            recent_entries=recent_entries,
            total_entries=total_entries,
            month_entries=month_entries,
            most_common_mood=most_common_mood
        )


    except sqlite3.Error as e:

        print(
            "Dashboard error:",
            e
        )

        flash(
            "Unable to load dashboard.",
            "error"
        )

        return redirect(url_for("login"))


    finally:

        cursor.close()
        connection.close()


# ==========================================
# NEW ENTRY
# ==========================================

@app.route("/new-entry", methods=["GET", "POST"])
@login_required
def new_entry():

    if request.method == "POST":

        entry_date = request.form.get(
            "entry_date",
            ""
        )

        title = request.form.get(
            "title",
            ""
        ).strip()

        mood = request.form.get(
            "mood",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()


        if not entry_date or not title or not mood or not content:

            flash(
                "Please fill in all fields.",
                "error"
            )

            return redirect(
                url_for("new_entry")
            )


        connection = get_db_connection()

        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO diary_entries
                (
                    user_id,
                    entry_date,
                    title,
                    mood,
                    content
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    entry_date,
                    title,
                    mood,
                    content
                )
            )

            connection.commit()


            flash(
                "Diary entry created successfully.",
                "success"
            )

            return redirect(
                url_for("entries")
            )


        except sqlite3.Error as e:

            connection.rollback()

            print(
                "Create entry error:",
                e
            )

            flash(
                "Unable to create diary entry.",
                "error"
            )

            return redirect(
                url_for("new_entry")
            )


        finally:

            cursor.close()
            connection.close()


    return render_template(
        "entry_form.html",
        mode="new",
        entry=None,
        today=date.today().isoformat()
    )


# ==========================================
# ALL ENTRIES
# ==========================================

@app.route("/entries")
@login_required
def entries():

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                entry_id,
                entry_date,
                title,
                mood,
                content
            FROM diary_entries
            WHERE user_id = ?
            ORDER BY entry_date DESC, entry_id DESC
            """,
            (session["user_id"],)
        )

        all_entries = cursor.fetchall()


        return render_template(
            "entries.html",
            entries=all_entries
        )


    except sqlite3.Error as e:

        print(
            "Entries error:",
            e
        )

        flash(
            "Unable to load diary entries.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )


    finally:

        cursor.close()
        connection.close()


# ==========================================
# VIEW SINGLE ENTRY
# ==========================================

@app.route("/entry/<int:entry_id>")
@login_required
def view_entry(entry_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                entry_id,
                entry_date,
                title,
                mood,
                content
            FROM diary_entries
            WHERE entry_id = ?
            AND user_id = ?
            """,
            (
                entry_id,
                session["user_id"]
            )
        )

        entry = cursor.fetchone()


        if not entry:

            flash(
                "Diary entry not found.",
                "error"
            )

            return redirect(
                url_for("entries")
            )


        return render_template(
            "view_entry.html",
            entry=entry
        )


    except sqlite3.Error as e:

        print(
            "View entry error:",
            e
        )

        flash(
            "Unable to open diary entry.",
            "error"
        )

        return redirect(
            url_for("entries")
        )


    finally:

        cursor.close()
        connection.close()


# ==========================================
# EDIT ENTRY
# ==========================================

@app.route(
    "/entry/<int:entry_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_entry(entry_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        # ----------------------------------
        # GET EXISTING ENTRY
        # ----------------------------------

        cursor.execute(
            """
            SELECT
                entry_id,
                entry_date,
                title,
                mood,
                content
            FROM diary_entries
            WHERE entry_id = ?
            AND user_id = ?
            """,
            (
                entry_id,
                session["user_id"]
            )
        )

        entry = cursor.fetchone()


        if not entry:

            flash(
                "Diary entry not found.",
                "error"
            )

            return redirect(
                url_for("entries")
            )


        # ----------------------------------
        # UPDATE ENTRY
        # ----------------------------------

        if request.method == "POST":

            entry_date = request.form.get(
                "entry_date",
                ""
            )

            title = request.form.get(
                "title",
                ""
            ).strip()

            mood = request.form.get(
                "mood",
                ""
            ).strip()

            content = request.form.get(
                "content",
                ""
            ).strip()


            if not entry_date or not title or not mood or not content:

                flash(
                    "Please fill in all fields.",
                    "error"
                )

                return render_template(
                    "entry_form.html",
                    mode="edit",
                    entry=entry,
                    today=date.today().isoformat()
                )


            cursor.execute(
                """
                UPDATE diary_entries
                SET
                    entry_date = ?,
                    title = ?,
                    mood = ?,
                    content = ?
                WHERE entry_id = ?
                AND user_id = ?
                """,
                (
                    entry_date,
                    title,
                    mood,
                    content,
                    entry_id,
                    session["user_id"]
                )
            )


            connection.commit()


            flash(
                "Diary entry updated successfully.",
                "success"
            )


            return redirect(
                url_for(
                    "view_entry",
                    entry_id=entry_id
                )
            )


        # ----------------------------------
        # EDIT PAGE
        # ----------------------------------

        return render_template(
            "entry_form.html",
            mode="edit",
            entry=entry,
            today=date.today().isoformat()
        )


    except sqlite3.Error as e:

        connection.rollback()

        print(
            "Edit entry error:",
            e
        )

        flash(
            "Unable to update diary entry.",
            "error"
        )

        return redirect(
            url_for("entries")
        )


    finally:

        cursor.close()
        connection.close()


# ==========================================
# DELETE ENTRY
# ==========================================

@app.route(
    "/entry/<int:entry_id>/delete",
    methods=["POST"]
)
@login_required
def delete_entry(entry_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM diary_entries
            WHERE entry_id = ?
            AND user_id = ?
            """,
            (
                entry_id,
                session["user_id"]
            )
        )

        connection.commit()


        flash(
            "Diary entry deleted successfully.",
            "success"
        )

        return redirect(
            url_for("entries")
        )


    except sqlite3.Error as e:

        connection.rollback()

        print(
            "Delete entry error:",
            e
        )

        flash(
            "Unable to delete diary entry.",
            "error"
        )

        return redirect(
            url_for("entries")
        )


    finally:

        cursor.close()
        connection.close()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )