import os
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from dbHelper import dbHelper
from helpers import login_required, warning
from flask_session import Session
from datetime import date

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = dbHelper("TT.db")



@app.route("/")
def home():
    #users = db.execute("select * from users;")

    #for user in users:
    #app.logger.info("user:", users)

    return render_template("index.html")

@app.route("/")
@login_required
def index():

    userId = session["user_id"]
    #userRows = db.execute("SELECT cash FROM users WHERE users.id=?", userId)
    #currentShares = db.execute("SELECT symbol, quantity FROM shares WHERE userId = ? ", userId)
    #data2 = {}
    #totalSum = 0
    #i = 0
    #for share in currentShares:
    #    data = lookup(share.get("symbol"))
    #    price = usd(data.get("price"))
    #    currentShares[i]["price"] = price
    #    sum = usd(float(data.get("price")) * float(share.get("quantity")))
    #    totalSum += float(data.get("price")) * float(share.get("quantity"))
    #    currentShares[i]["totalPrice"] = sum
    #    i += 1

    #roundedSum = totalSum
    #currentCash = userRows[0]["cash"]
    #data2["sum"] = usd(currentCash + roundedSum)
    #data2["cash"] = usd(currentCash)

    return render_template("index.html")#, data = currentShares, data2 = data2


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
