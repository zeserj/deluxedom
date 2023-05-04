import os
import csv

#TODO: switch from cs50 SQL to sqlite3
import sqlite3
from cs50 import SQL

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from dateutil import parser
from dotenv import load_dotenv

from helpers import apology, login_required, domain_search, validate, is_domain, generate_5char_words

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create database if it doesn't exist

conn = sqlite3.connect('domain.db')
db = conn.cursor()

db.execute('''
            CREATE TABLE IF NOT EXISTS domains (
	            [name] TEXT NOT NULL PRIMARY KEY,
	            [category]	INTEGER NOT NULL,
	            [available]	BOOLEAN,
	            [expires_at]	DATETIME,
	            [checked_at]	DATETIME,
	            [registry_statuses]	TEXT)
            ''')
db.execute('''
            CREATE TABLE IF NOT EXISTS history (
                [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                [user_id] INTEGER NOT NULL, 
                [domain_name] TEXT NOT NULL, 
                [available] BOOLEAN NOT NULL, 
                [expires_at] DATETIME, 
                [checked_at] DATETIME NOT NULL)
            ''')

db.execute('''
            CREATE TABLE IF NOT EXISTS users (
	            [id]	INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	            [username]	TEXT NOT NULL,
	            [hash]	TEXT NOT NULL, 'isAdmin' TEXT NOT NULL DEFAULT 'no')
            ''')

conn.commit()

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///domain.db")

# Make sure API key is set
load_dotenv()
if not os.getenv("API_EMAIL"):
    raise RuntimeError("API_EMAIL is missing from .env")
if not os.getenv("API_KEY"):
    raise RuntimeError("API_KEY is missing from .env")
if not os.getenv('API_ACCOUNT_ID'):
    raise RuntimeError("API_ACCOUNT_ID is missing from .env")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show search bar for domain"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if symbol is entered
        if not request.form.get("domain"):
            return apology("MISSING DOMAIN", 400)

        # Check if domain is valid
        if not is_domain(request.form.get("domain")):
            return apology("INVALID DOMAIN", 400)

        # Get domain
        domain = domain_search(request.form.get("domain"))

        # Show search result of domain

        if domain["available"]==True:

            # Add the search to the history database
            db.execute("INSERT INTO history (user_id, domain_name, available, checked_at) VALUES (?,?,?,?)", session["user_id"], domain["name"], domain["available"], date.today())

            return render_template("indexed.html", name=domain["name"], available=domain["available"])

        else:
            # Add the search to the history database
            db.execute("INSERT INTO history (user_id, domain_name, available, expires_at, checked_at) VALUES (?,?,?,?,?)", session["user_id"], domain["name"], domain["available"], domain["expires_at"], date.today())

            return render_template("indexed.html", name=domain["name"], available=domain["available"], expires_at=domain["expires_at"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


@app.route("/history")
@login_required
def history():
    """Show history of domain searches"""

    domains = db.execute("SELECT domain_name, available, expires_at, checked_at FROM history WHERE user_id = ?", session["user_id"])

    # Show table with current holdings
    return render_template("history.html", domains=domains)


@app.route("/char3")
@login_required
def char3():
    """Show available 3 character domains"""

    domains = db.execute("SELECT name, available, expires_at, checked_at FROM domains WHERE available = 1 AND category = ?", 3)

    # Show table with available 3 character domains
    return render_template("char3.html", domains=domains)


@app.route("/char4")
@login_required
def char4():
    """Show available 4 character domains"""

    domains = db.execute("SELECT name, available, expires_at, checked_at FROM domains WHERE available = 1 AND category = ?", 4)

    # Show table with available 3 character domains
    return render_template("char4.html", domains=domains)


@app.route("/char5")
@login_required
def char5():
    """Show available 5 character domains"""

    domains = db.execute("SELECT name, available, expires_at, checked_at FROM domains WHERE available = 1 AND category = ?", 5)

    # Show table with available 5 character domains
    return render_template("char5.html", domains=domains)


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """Show the administration page for the website"""

    # Check if the user trying to access the page is an admin
    if session["admin"] == "no":
        return apology("No access! Please login as admin!", 403)
    if session["admin"] == "yes":

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":

            # Check to see which action was selected
            if request.form.get("actions") == "scrabble":

                # Open the words document
                with open('words.csv',newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for word in reader:
                        # check if word is already in the database
                        if (not db.execute("SELECT * FROM domains WHERE name = ?", f"{word[0].lower()}.com")):
                            db.execute("INSERT INTO domains (name, category) VALUES (?,?)", f"{word[0].lower()}.com", len(word[0]))
                            print(f"Inserted {word}.com into Database", )
                        else:
                            print(f"{word[0].lower()}.com already in Database")
                        
                # Flash message of succesful action
                flash("You have successfully added the Collins Scrabble Words!")
            
            # Check to see which action was selected
            if request.form.get("actions") == "5char":

                for word in generate_5char_words():
                    # check if word is already in the database
                    if (not db.execute("SELECT * FROM domains WHERE name = ?", f"{word}.com")):
                        db.execute("INSERT INTO domains (name, category) VALUES (?,?)", f"{word}.com", len(word))
                        print(f"Added {word}.com to database")
                    else:
                        print(f"{word}.com already in database")
                        
                # Flash message of succesful action
                flash("You have successfully added the generated domains!")

            if request.form.get("actions") == "check":

                # Get all domains in database
                domains = db.execute("SELECT * FROM domains")

                for domain in domains:
                    # Check to see if the domain has ever been checked or if the domain used to be available

                    if (domain["available"] == 1 or domain["available"] == None):

                        # Perform a check on the domain
                        domain_update = domain_search(domain["name"])

                        # Update the records only if domain_update is not None

                        if not(domain_update == None):
                            # Update the record depending on availability
                            if domain_update["available"] == 1:
                                db.execute("UPDATE domains SET available=?, checked_at=? WHERE name=?", domain_update["available"], date.today(), domain_update["name"])
                            else:
                                db.execute("UPDATE domains SET available=?, expires_at=?, checked_at=?, registry_statuses=? WHERE name=?", domain_update["available"], domain_update["expires_at"], date.today(), domain_update["registry_statuses"], domain_update["name"])

                    elif (domain["available"] == 0 and date.today() > parser.parse(domain["expires_at"]).date()):
                        # Perform a check on the domain
                        domain_update = domain_search(domain["name"])

                        # Update the records only if domain_update is not None

                        if not(domain_update == None):
                            # Update the record depending on availability
                            if domain_update["available"] == 1:
                                db.execute("UPDATE domains SET available=?, checked_at=? WHERE name=?", domain_update["available"], date.today(), domain_update["name"])
                            else:
                                db.execute("UPDATE domains SET available=?, expires_at=?, checked_at=?, registry_statuses=? WHERE name=?", domain_update["available"], domain_update["expires_at"], date.today(), domain_update["registry_statuses"],domain_update["name"])

                # Flash message of succesful action
                flash("You have successfully checked domains!")

            # Redirect user to admin page
            return redirect("/admin")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("admin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember admin status of user that has logged in
        session["admin"] = rows[0]["isAdmin"]

        # Flash message of succesful login
        flash("You are now logged in!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("MISSING USERNAME", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("MISSING PASSWORD", 400)

        # Ensure the password was confirmed
        elif not request.form.get("confirmation"):
            return apology("MISSING CONFIRMATION", 400)

        # Ensure password was submitted
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("PASSWORDS DON'T MATCH", 400)

        # Validate password to have at least one number, at least one uppercase and one lowercase character, at least one special symbol and 8 to 32 characters long
        elif not validate(request.form.get("password")):
            return apology("Password should have:\n* At least one number.\n* At least one uppercase and one lowercase character.\n* At least one special symbol.\n* Between 8 to 32 characters.", 403)

        # Ensure username doesn't exists
        if len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))) == 1:
            return apology("USERNAME NOT AVAILABLE", 400)

        # Add user and password hash to database
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Check if the user id is 1, then make him admin as well
        if rows[0]["id"] == 1:
            db.execute("UPDATE users SET isAdmin = 'yes' WHERE id = 1")

        # Remember admin status of user that has logged in
        session["admin"] = rows[0]["isAdmin"]

        # Flash message of succesful registration
        flash("You were successfully registered!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

