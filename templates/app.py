from pathlib import Path
from html import escape

from flask import Flask, abort, redirect, request, send_file, send_from_directory, session
import mysql.connector
from mysql.connector import Error

BASE_DIR = Path(__file__).resolve().parent
PRIVATE_RESUME = BASE_DIR / "private" / "Yash_Resume.pdf"

app = Flask(__name__)
app.secret_key = "change_this_secret_key_for_yash_portfolio"

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""  # XAMPP default MySQL password is blank
DB_NAME = "portfolio_db"

ALLOWED_HTML = {
    "index.html",
    "about.html",
    "projects.html",
    "project.html",
    "contact.html",
    "register.html",
}

ALLOWED_FILES = {"style.css", "script.js"}


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def ensure_database():
    """Create database and tables automatically when XAMPP MySQL is running."""
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.close()
    conn.close()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS registrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(120) NOT NULL,
            email VARCHAR(120) NOT NULL,
            phone VARCHAR(25) NOT NULL,
            purpose VARCHAR(80) NOT NULL,
            linkedin VARCHAR(255),
            github VARCHAR(255),
            message TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(80) NOT NULL,
            last_name VARCHAR(80),
            email VARCHAR(120) NOT NULL,
            subject VARCHAR(180) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def page_shell(title, body_html, body_class="register-page"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(title)} · Yash P Shetty</title>
  <link rel="stylesheet" href="/style.css" />
</head>
<body class="{body_class}">
<nav class="navbar">
  <div class="nav-inner">
    <a class="nav-logo" href="/index.html"><span class="logo-mark">YS</span><span>yash<span style="color:var(--primary)">.</span>portfolio</span></a>
    <ul class="nav-links">
      <li><a href="/index.html">Home</a></li>
      <li><a href="/about.html">About</a></li>
      <li><a href="/projects.html">Projects</a></li>
      <li><a href="/contact.html">Contact</a></li>
      <li><a href="/register.html" class="nav-cta">Register</a></li>
    </ul>
  </div>
</nav>
<main>{body_html}</main>
<footer>
  <div class="footer-inner">
    <p>© Yash P Shetty.</p>
    <ul class="footer-links">
      <li><a href="mailto:shettyyashp@gmail.com">Email</a></li>
      <li><a href="https://github.com/yashpshetty" target="_blank" rel="noreferrer">GitHub</a></li>
      <li><a href="https://linkedin.com/in/yash-p-shetty-9a8aa0354" target="_blank" rel="noreferrer">LinkedIn</a></li>
      <li><a href="/register.html">Register</a></li>
    </ul>
  </div>
</footer>
<script src="/script.js"></script>
</body>
</html>"""


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
        return page_shell(
            "Registration Error",
            """
            <section><div class="container"><div class="error-box">
            Please fill Full Name, Email, Phone Number and Purpose.
            </div><a class="btn btn-primary" href="/register.html">Go Back</a></div></section>
            """,
        ), 400

    try:
        ensure_database()
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
        return page_shell(
            "Database Error",
            f"""
            <section><div class="container"><div class="error-box">
            Database error: {escape(str(err))}<br>
            Start XAMPP MySQL, then run <strong>python app.py</strong> again.
            </div><a class="btn btn-primary" href="/register.html">Try Again</a></div></section>
            """,
        ), 500

    session["registered_for_resume"] = True
    session["registered_email"] = email
    session["registered_name"] = full_name

    return redirect("/registration-success")


@app.route("/registration-success")
def registration_success():
    name = escape(session.get("registered_name", "Visitor"))
    body = f"""
    <section>
      <div class="container">
        <div class="form-card reveal" style="max-width:760px;margin:auto;">
          <div class="success-box">
            ✅ Registration successful, {name}. Your details are saved in MySQL.
          </div>
          <h1 style="font-size:clamp(2rem,5vw,3.5rem);">Resume Download Started</h1>
          <p style="margin:1rem 0 1.4rem;">If the resume does not download automatically, click the button below.</p>
          <a class="btn btn-primary" href="/download-resume">Download Resume Now <span class="arrow">→</span></a>
          <a class="btn btn-outline" href="/admin/registrations" style="margin-left:.6rem;">View Registered Users</a>
          <iframe src="/download-resume" style="display:none;width:0;height:0;border:0;"></iframe>
        </div>
      </div>
    </section>
    """
    return page_shell("Registration Successful", body, "register-page")


@app.route("/download-resume")
def download_resume():
    if not session.get("registered_for_resume"):
        return redirect("/register.html")

    if not PRIVATE_RESUME.exists():
        return page_shell(
            "Resume Missing",
            """
            <section><div class="container"><div class="error-box">
            Resume file not found. Keep the file at <strong>private/Yash_Resume.pdf</strong>.
            </div></div></section>
            """,
        ), 404

    return send_file(
        PRIVATE_RESUME,
        as_attachment=True,
        download_name="Yash_P_Shetty_Resume.pdf",
        mimetype="application/pdf",
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
        return page_shell(
            "Contact Error",
            """
            <section><div class="container"><div class="error-box">
            Please fill First Name, Email, Subject and Message.
            </div><a class="btn btn-primary" href="/contact.html">Go Back</a></div></section>
            """,
            "contact-page",
        ), 400

    try:
        ensure_database()
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
        return page_shell(
            "Database Error",
            f"""
            <section><div class="container"><div class="error-box">
            Database error: {escape(str(err))}<br>
            Start XAMPP MySQL, then run <strong>python app.py</strong> again.
            </div><a class="btn btn-primary" href="/contact.html">Try Again</a></div></section>
            """,
            "contact-page",
        ), 500

    return redirect("/contact-success")


@app.route("/contact-success")
def contact_success():
    body = """
    <section>
      <div class="container">
        <div class="form-card reveal" style="max-width:760px;margin:auto;">
          <div class="success-box">✅ Message sent successfully. The contact details are saved in MySQL.</div>
          <h1 style="font-size:clamp(2rem,5vw,3.5rem);">Thank You!</h1>
          <p style="margin:1rem 0 1.4rem;">You can view submitted contact messages from the admin page.</p>
          <a class="btn btn-primary" href="/admin/contact-messages">View Contact Messages</a>
          <a class="btn btn-outline" href="/contact.html" style="margin-left:.6rem;">Back to Contact</a>
        </div>
      </div>
    </section>
    """
    return page_shell("Message Sent", body, "contact-page")


@app.route("/admin")
def admin_home():
    body = """
    <section>
      <div class="container">
        <div class="form-card reveal" style="max-width:840px;margin:auto;">
          <span class="label">Local Admin</span>
          <h1 style="font-size:clamp(2rem,5vw,3.5rem);">Portfolio Records</h1>
          <p style="margin:1rem 0;">Use these pages while running Flask with XAMPP MySQL.</p>
          <div class="admin-actions">
            <a class="btn btn-primary" href="/admin/registrations">View Registered Users</a>
            <a class="btn btn-outline" href="/admin/contact-messages">View Contact Messages</a>
          </div>
        </div>
      </div>
    </section>
    """
    return page_shell("Admin", body, "register-page")


def table_page(title, headers, rows, body_class="register-page"):
    head_html = "".join(f"<th>{escape(h)}</th>" for h in headers)
    row_html = ""
    if rows:
        for row in rows:
            row_html += "<tr>" + "".join(f"<td>{escape(str(col or ''))}</td>" for col in row) + "</tr>"
    else:
        row_html = f"<tr><td colspan='{len(headers)}'>No records found.</td></tr>"

    body = f"""
    <section>
      <div class="container">
        <div class="form-card reveal">
          <span class="label">Local Admin</span>
          <h1 style="font-size:clamp(2rem,5vw,3.5rem);">{escape(title)}</h1>
          <p style="margin:.8rem 0 1rem;">These records are read from the MySQL database <strong>{DB_NAME}</strong>.</p>
          <div class="admin-actions">
            <a class="btn btn-outline" href="/admin">Admin Home</a>
            <a class="btn btn-outline" href="/index.html">Back to Portfolio</a>
          </div>
          <div class="admin-table-wrap">
            <table class="admin-table">
              <thead><tr>{head_html}</tr></thead>
              <tbody>{row_html}</tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
    """
    return page_shell(title, body, body_class)


@app.route("/admin/registrations")
def admin_registrations():
    try:
        ensure_database()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, full_name, email, phone, purpose, linkedin, github, message, registered_at
            FROM registrations
            ORDER BY registered_at DESC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as err:
        return page_shell("Database Error", f"<section><div class='container'><div class='error-box'>{escape(str(err))}</div></div></section>"), 500

    headers = ["ID", "Full Name", "Email", "Phone", "Purpose", "LinkedIn", "GitHub", "Message", "Registered At"]
    return table_page("Registered Users", headers, rows, "register-page")


@app.route("/admin/contact-messages")
def admin_contact_messages():
    try:
        ensure_database()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, first_name, last_name, email, subject, message, created_at
            FROM contact_messages
            ORDER BY created_at DESC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as err:
        return page_shell("Database Error", f"<section><div class='container'><div class='error-box'>{escape(str(err))}</div></div></section>", "contact-page"), 500

    headers = ["ID", "First Name", "Last Name", "Email", "Subject", "Message", "Created At"]
    return table_page("Contact Messages", headers, rows, "contact-page")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    try:
        ensure_database()
        print("Database and tables are ready.")
    except Error as err:
        print(f"Database setup skipped/error: {err}")
        print("Start XAMPP MySQL, then run python app.py again.")
    app.run(debug=True)
