import os
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from dailyTracking import DailyTracking

from dbHelper import dbHelper
from helpers import login_required, warning
from flask_session import Session
from datetime import date
from enum import Enum
from calendarLogic import CalendarLogic
from weekCalculator import WeekCalculator 


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = dbHelper("TT.db")
dailyTrack = DailyTracking(db, session)
weekCalculator = WeekCalculator(db, session, dailyTrack)

types = { 'start':1, 'end':2 }

class timestampTypes(Enum):
     START = 1
     END = 2


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():

    total = 0
    rows = dailyTrack.getTodayTrackings()
    actions = dailyTrack.getTimeActionsDict(rows)
    availableAactions = dailyTrack.checkAvailableActions(rows)
    total = dailyTrack.calcHours(rows)

    userId = session["user_id"]
    if request.method == 'POST':
        if request.form.get('actionStart') == 'valueStart':
            dailyTrack.saveTimeLog(1, "startDay")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
            actions = dailyTrack.getTimeActionsDict(rows)
        elif request.form.get('actionLunchStart') == 'valueLunchStart':
            dailyTrack.saveTimeLog(2, "startLunch")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
            actions = dailyTrack.getTimeActionsDict(rows)
        elif request.form.get('actionLunchEnd') == 'valueLunchEnd':
            dailyTrack.saveTimeLog(1, "finishLunch")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
            actions = dailyTrack.getTimeActionsDict(rows)
        elif request.form.get('actionEnd') == 'valueEnd':
            dailyTrack.saveTimeLog(2, "finishDay")
            rows = dailyTrack.getTodayTrackings()
            availableAactions = dailyTrack.checkAvailableActions(rows)
            actions = dailyTrack.getTimeActionsDict(rows)
            total = dailyTrack.calcHours(rows)
    elif request.method == 'GET':
        return render_template('index.html', actions=availableAactions, actionsList=actions, total=total)
    return render_template("index.html", actions=availableAactions, actionsList=actions, total=total)

@app.route("/month", methods=['GET', 'POST'])
@login_required
def month():
    CalendarLogic.setFirsDayOfWeek(6) #create config with start day
    if request.method == 'POST':
        yearFromForm = int(request.form.get('yearField'))
        monthFromForm = CalendarLogic.convertMonthToNumber(request.form.get('monthField'))
        if request.form.get('actionLeft') == 'valueLeft':
            selectedMonth, selectedYear = CalendarLogic.previousMonthAndYear(yearFromForm, monthFromForm) #datetime.today().year, datetime.today().month)
            selectedMonthName = CalendarLogic.MONTHS[selectedMonth-1]
            days = CalendarLogic.monthDaysWithWeekday(selectedYear, selectedMonth)
            return render_template("month.html", monthName = selectedMonthName, year = selectedYear, monthDays = days)
        if request.form.get('actionRight') == 'valueRight':
            selectedMonth, selectedYear = CalendarLogic.nextMonthAndYear(yearFromForm, monthFromForm)
            selectedMonthName = CalendarLogic.MONTHS[selectedMonth-1]
            days = CalendarLogic.monthDaysWithWeekday(selectedYear, selectedMonth)
            return render_template("month.html", monthName = selectedMonthName, year = selectedYear, monthDays = days)
        
        days = CalendarLogic.monthDaysWithWeekday(yearFromForm, monthFromForm)
        for week in days:
            for selectedDay in week:
                if selectedDay == 0:
                    continue
                if f'day{selectedDay}' in request.form:
                    session['selectedDate'] = {'year':yearFromForm, 'month':monthFromForm, 'day':selectedDay}
                    return redirect("/day")

            
    if request.method == 'GET':
        currentMonth = datetime.today().month
        currentMonthName = CalendarLogic.MONTHS[datetime.today().month-1]
        currentYear = datetime.today().year
        days = CalendarLogic.monthDaysWithWeekday(currentYear, currentMonth)
        return render_template("month.html", monthName = currentMonthName, year = currentYear, monthDays = days)

@app.route("/day", methods=['GET', 'POST'])
@login_required
def day():
    selectedDate = session.get('selectedDate')
    dateString = "{year}-{month}-{day}".format(**selectedDate)
    rows = dailyTrack.getTheDayTrackings(dateString)
    actions = dailyTrack.getTimeActionsDict(rows)
    total = dailyTrack.calcHours(rows)
    return render_template("day.html", actionsList=actions, total=total, selectedDate=dateString)

@app.route("/week", methods=['GET', 'POST'])
@login_required
def week():
    #weekDays = weekCalculator.getCurrentWeekDatesStrings()
    #rows = weekCalculator.getWeekTrackings()
    #weekCalculator.getWeekHours()
    return render_template("week.html" )

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
