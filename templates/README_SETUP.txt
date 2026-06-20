Yash P Shetty Portfolio - XAMPP + Flask + MySQL Setup

1. Copy this folder to any location, for example:
   C:\xampp\htdocs\yash_portfolio_xampp_updated

2. Open XAMPP Control Panel and start:
   - Apache  (optional, useful for phpMyAdmin)
   - MySQL   (required)

3. Create the database:
   - Open http://localhost/phpmyadmin
   - Click SQL
   - Paste the code from database.sql
   - Click Go

4. Install Python packages:
   Open terminal inside this project folder and run:
   pip install -r requirements.txt

5. Run the Flask app:
   python app.py

6. Open the portfolio:
   http://127.0.0.1:5000

Important:
- To make resume registration protection work, open the site using Flask: http://127.0.0.1:5000
- Do not open index.html directly using file:/// because backend registration and resume protection will not work.
- The resume PDF is kept inside the private folder and is served only by /download-resume after registration.
- If you change your MySQL password, edit DB_CONFIG in app.py.
