YASH PORTFOLIO - XAMPP + FLASK + MYSQL SETUP
================================================

IMPORTANT:
Do not open index.html directly for registration/contact testing.
You must run the Flask app and open http://127.0.0.1:5000

1) Start XAMPP
--------------
Open XAMPP Control Panel and start MySQL.
Apache is not required for this Flask version.

2) Install Python packages
--------------------------
Open terminal inside this project folder and run:

pip install -r requirements.txt

3) Run Flask app
----------------
python app.py

Then open:
http://127.0.0.1:5000

4) Registration and resume download
-----------------------------------
Click Register, fill the form, and submit.
After successful registration:
- Details are saved in MySQL table: registrations
- Success message is shown
- Resume download starts automatically

If automatic download does not start, click Download Resume Now on the success page.

5) Contact form
---------------
Open Contact page, fill the form, and submit.
After successful submission:
- Details are saved in MySQL table: contact_messages
- Success message is shown

6) View saved users and messages
--------------------------------
In browser while Flask app is running:

Registered users:
http://127.0.0.1:5000/admin/registrations

Contact messages:
http://127.0.0.1:5000/admin/contact-messages

Or in phpMyAdmin:
http://localhost/phpmyadmin

Click:
portfolio_db -> registrations -> Browse
portfolio_db -> contact_messages -> Browse

7) If data is not saving
------------------------
Check these points:
- XAMPP MySQL is running.
- You opened the site using http://127.0.0.1:5000, not by double-clicking index.html.
- The form action must be /register and /contact.
- Keep Yash_Resume.pdf inside private folder.

8) GitHub / Render note
-----------------------
This XAMPP + MySQL registration works locally on your laptop.
Render Static Site cannot run Flask or XAMPP MySQL.
For Render, you need Render Web Service + an online database.
