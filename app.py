import os
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from dailyTracking import dailyTracking

from dbHelper import dbHelper
from helpers import login_required, warning
from flask_session import Session
from datetime import date
from enum import Enum

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = dbHelper("TT.db")
dailyTrack = dailyTracking(db, session)

types = { 'start':1, 'end':2 }

class timestampTypes(Enum):
     START = 1
     END = 2

#@app.route("/")
#def home():
    #users = db.execute("select * from users;")

    #for user in users:
    #app.logger.info("user:", users)

    #return render_template("index.html")

@app.route("/", methods=['GET', 'POST'])
@login_required
def index():

    rows = dailyTrack.getTodayTrackings()
    availableAactions = dailyTrack.checkAvailableActions(rows)
    print(availableAactions)

    userId = session["user_id"]
    if request.method == 'POST':
        if request.form.get('actionStart') == 'valueStart':
            dailyTrack.saveTimeLog(1, "startDay")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
        elif request.form.get('actionLunchStart') == 'valueLunchStart':
            dailyTrack.saveTimeLog(2, "startLunch")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
        elif request.form.get('actionLunchEnd') == 'valueLunchEnd':
            dailyTrack.saveTimeLog(1, "finishLunch")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
        elif request.form.get('actionEnd') == 'valueEnd':
            dailyTrack.saveTimeLog(2, "finishDay")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
    elif request.method == 'GET':
        return render_template('index.html', actions=availableAactions)
    
    return render_template("index.html", actions=availableAactions)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return warning("must provide username", 400)

        username = request.form.get("username")
        rows = db.execute(f"SELECT * FROM users WHERE username = '{username}';")
        if len(rows) != 0:
            return warning("This username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return warning("must provide password", 400)

         # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return warning("must provide confirmation", 400)

        elif not  request.form.get("password") == request.form.get("confirmation"):
            return warning("Password and  confirmation do not match", 400)

        else:
            # Query database for username
            hash = generate_password_hash(request.form.get("password"))
            userName = request.form.get("username")
            fname = request.form.get("firstname")
            lname = request.form.get("lastname")
            curdate = date.today()
            db.executePush("INSERT INTO users (username,  firstname, lastname, key, date) VALUES(?,?,?,?,?);", [userName, fname, lname, hash, curdate])
    else:
        return render_template("register.html")

    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return warning("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return warning("must provide password", 403)

        # Query database for username
        userName = request.form.get("username")
        rows = db.execute(f"SELECT * FROM users WHERE username = '{userName}';")

        # Ensure username exists and password is correct
        data = list(rows[0])
        if len(rows) != 1 or not check_password_hash(data[4], request.form.get("password")):
            return warning("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = data[0]

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
