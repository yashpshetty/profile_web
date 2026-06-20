from pathlib import Path

from flask import Flask, abort, redirect, request, send_file, send_from_directory, session
import mysql.connector
from mysql.connector import Error

BASE_DIR = Path(__file__).resolve().parent
PRIVATE_RESUME = BASE_DIR / "private" / "Yash_Resume.pdf"

app = Flask(__name__)
app.secret_key = "change_this_secret_key_for_your_portfolio"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          # XAMPP default MySQL password is blank
    "database": "portfolio_db"
}

ALLOWED_HTML = {
    "index.html",
    "about.html",
    "projects.html",
    "project.html",
    "contact.html",
    "register.html",
}

ALLOWED_FILES = {
    "style.css",
    "script.js",
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def serve_public_file(filename):
    """Serve only safe public files. The private resume folder is not exposed."""
    if filename in ALLOWED_HTML or filename in ALLOWED_FILES:
        return send_from_directory(BASE_DIR, filename)

    if filename.startswith("images/"):
        return send_from_directory(BASE_DIR, filename)

    # Do not serve private/Yash_Resume.pdf directly.
    abort(404)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return send_from_directory(BASE_DIR, "register.html")

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    purpose = request.form.get("purpose", "").strip()
    linkedin = request.form.get("linkedin", "").strip()
    github = request.form.get("github", "").strip()
    message = request.form.get("message", "").strip()

    if not full_name or not email or not phone or not purpose:
        return "Please fill Full Name, Email, Phone Number and Purpose.", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO registrations
            (full_name, email, phone, purpose, linkedin, github, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (full_name, email, phone, purpose, linkedin, github, message)
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as err:
        return f"Database error: {err}. Make sure XAMPP MySQL is running and database.sql is imported.", 500

    # Mark this visitor as registered for the current browser session.
    session["registered_for_resume"] = True
    session["registered_email"] = email
    session["registered_name"] = full_name

    # After successful registration, download the resume.
    return redirect("/download-resume")


@app.route("/download-resume")
def download_resume():
    if not session.get("registered_for_resume"):
        return redirect("/register.html")

    if not PRIVATE_RESUME.exists():
        return "Resume file not found in private folder.", 404

    return send_file(
        PRIVATE_RESUME,
        as_attachment=True,
        download_name="Yash_P_Shetty_Resume.pdf",
        mimetype="application/pdf"
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return send_from_directory(BASE_DIR, "contact.html")

    fname = request.form.get("fname", "").strip()
    lname = request.form.get("lname", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not fname or not email or not subject or not message:
        return "Please fill First Name, Email, Subject and Message.", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO contact_messages
            (first_name, last_name, email, subject, message)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (fname, lname, email, subject, message)
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as err:
        return f"Database error: {err}. Make sure XAMPP MySQL is running and database.sql is imported.", 500

    return """
    <script>
      alert('Message saved successfully. Thank you for contacting Yash P Shetty.');
      window.location.href = '/contact.html';
    </script>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
