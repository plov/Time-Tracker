import os
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from dailyTracking import DailyTracking

from dbHelper import dbHelper
from helpers import login_required, validate_form, warning
from flask_session import Session
from datetime import date
from calendarLogic import CalendarLogic
from weekCalculator import WeekCalculator 
from constants import constants


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = dbHelper("TT.db")
dailyTrack = DailyTracking(db, session)
weekCalculator = WeekCalculator(db, session, dailyTrack)

types = { 'start':1, 'end':2 }

@app.route("/", methods=['GET', 'POST'])
@login_required
def index():

    total = 0
    rows = dailyTrack.today_trackings()
    actions = dailyTrack.time_points_list_of_dict(rows)
    availableAactions = dailyTrack.check_available_points(rows)
    total = dailyTrack.calc_day_hours(rows)
    result = dailyTrack.check_not_finished_day()

    if request.method == 'POST':
        if request.form.get('actionStart') == 'valueStart':
            dailyTrack.save_time_log(constants.START_TYPE, constants.START_DAY)
            rows = dailyTrack.today_trackings()
            availableAactions = dailyTrack.check_available_points(rows)
            actions = dailyTrack.time_points_list_of_dict(rows)
        elif request.form.get('actionLunchStart') == 'valueLunchStart':
            dailyTrack.save_time_log(constants.STOP_TYPE, constants.START_LUNCH)
            rows = dailyTrack.today_trackings()
            availableAactions = dailyTrack.check_available_points(rows)
            actions = dailyTrack.time_points_list_of_dict(rows)
        elif request.form.get('actionLunchEnd') == 'valueLunchEnd':
            dailyTrack.save_time_log(constants.START_TYPE, constants.FINISH_LUNCH)
            rows = dailyTrack.today_trackings()
            availableAactions = dailyTrack.check_available_points(rows)
            actions = dailyTrack.time_points_list_of_dict(rows)
        elif request.form.get('actionEnd') == 'valueEnd':
            dailyTrack.save_time_log(constants.STOP_TYPE, constants.FINISH_DAY)
            rows = dailyTrack.today_trackings()
            availableAactions = dailyTrack.check_available_points(rows)
            actions = dailyTrack.time_points_list_of_dict(rows)
            total = dailyTrack.calc_day_hours(rows)
    elif request.method == 'GET':
        return render_template('index.html', actions=availableAactions, actionsList=actions, total=total)
    return render_template("index.html", actions=availableAactions, actionsList=actions, total=total)

@app.route("/month", methods=['GET', 'POST'])
@login_required
def month():
    CalendarLogic.set_firs_day_of_week(constants.WEEK_START_DAY)
    if request.method == 'POST':
        yearFromForm = int(request.form.get('yearField'))
        monthFromForm = CalendarLogic.convert_month_to_number(request.form.get('monthField'))
        if request.form.get('actionLeft') == 'valueLeft':
            selectedMonth, selectedYear = CalendarLogic.previous_month_and_year(yearFromForm, monthFromForm)
            selectedMonthName = CalendarLogic.MONTHS[selectedMonth-1]
            days = CalendarLogic.month_days_with_weekday(selectedYear, selectedMonth)
            return render_template("month.html", monthName = selectedMonthName, year = selectedYear, monthDays = days)
        if request.form.get('actionRight') == 'valueRight':
            selectedMonth, selectedYear = CalendarLogic.next_month_and_year(yearFromForm, monthFromForm)
            selectedMonthName = CalendarLogic.MONTHS[selectedMonth-1]
            days = CalendarLogic.month_days_with_weekday(selectedYear, selectedMonth)
            return render_template("month.html", monthName = selectedMonthName, year = selectedYear, monthDays = days)
        
        days = CalendarLogic.month_days_with_weekday(yearFromForm, monthFromForm)
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
        days = CalendarLogic.month_days_with_weekday(currentYear, currentMonth)
        return render_template("month.html", monthName = currentMonthName, year = currentYear, monthDays = days)

@app.route("/day", methods=['GET', 'POST'])
@login_required
def day():
    selectedDate = session.get('selectedDate')
    noFormatDateString = "{year}-{month}-{day}".format(**selectedDate)
    dateObj = datetime.strptime(noFormatDateString, "%Y-%m-%d")
    dateString = date.strftime(dateObj, "%Y-%m-%d")
    rows = dailyTrack.select_date_trackings(dateString)
    actions = dailyTrack.time_points_list_of_dict(rows)
    total = dailyTrack.calc_day_hours(rows)
    if(dateObj.strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d')):
        return redirect("/")
    return render_template("day.html", actionsList=actions, total=total, selectedDate=dateString)

@app.route("/week", methods=['GET', 'POST'])
@login_required
def week():
    weekDays = weekCalculator.current_week_dates_2_strings()
    if request.method == 'POST':
        for selectedDay in weekDays:
            if f'day{selectedDay}' in request.form:
                date = datetime.strptime(selectedDay, "%Y-%m-%d")
                session['selectedDate'] = {'year':date.year, 'month':date.month, 'day':date.day}
                return redirect("/day")

    if request.method == 'GET':
        result = weekCalculator.week_hours()
        return render_template("week.html", firstDay = weekDays[0], lastDay = weekDays[-1], days=result[-1], totalWeeekHours=result[0])

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    print("register")
    if request.method == "POST":
        error = validate_form(request.form, ["username", "password", "confirmation"], "register.html")
        if error:
            return error
        
        username = request.form.get("username")
        rows = db.execute("""SELECT * 
                          FROM users 
                          WHERE username = ?;
                          """, [username])
        if len(rows) != 0:
            return warning("This username already exists", "register.html")

        elif not  request.form.get("password") == request.form.get("confirmation"):
            return warning("Password and  confirmation do not match", "register.html")
        else:
            hash = generate_password_hash(request.form.get("password"))
            userName = request.form.get("username")
            fname = request.form.get("firstname")
            lname = request.form.get("lastname")
            curdate = date.today()
            db.execute("""INSERT INTO users (username,  firstname, lastname, key, date) 
                       VALUES(?,?,?,?,?);
                       """, [userName, fname, lname, hash, curdate])
    else:
        return render_template("register.html")

    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        error = validate_form(request.form, ["username", "password"], "login.html")
        if error:
            return error

        username = request.form.get("username")
        rows = db.execute("""
                          SELECT * 
                          FROM users 
                          WHERE username = ?;
                          """, [username])
        print(f"rows: {rows}")

        if len(rows) != 1 or not check_password_hash(rows[0][4], request.form.get("password")):
            return warning("invalid username and/or password", "login.html")

        session["user_id"] = rows[0][0]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """change password"""
    if request.method == "POST":
        error = validate_form(request.form, ["username", "currenPassword", "newPassword", "confirmation"], "password.html")
        if error:
            return error
        
        if not  request.form.get("newPassword") == request.form.get("confirmation"):
            return warning("Password and  confirmation do not match", "password.html")
        
        userId = session["user_id"]
        formUserId = request.form.get("username")
        rows = db.execute("""
                          SELECT * 
                          FROM users 
                          WHERE username = ?;
                          """, [formUserId])
        if len(rows) != 1 or rows[0][0] != userId :
            return warning("invalid current username and/or password", "password.html")

        if len(rows) != 1 or not check_password_hash(rows[0][4], request.form.get("currenPassword")):
            return warning("invalid current password and/or username", "password.html",)
        hash = generate_password_hash(request.form.get("newPassword"))
        result = db.execute("""UPDATE users 
                            SET key = ? 
                            WHERE username = ?;
                            """, [hash, formUserId])
        if not result:
            return warning("Something went wrong", "password.html")
        flash("Your password has changed successfully!")
        return redirect("/")
    else:
        return render_template("password.html")
    
@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")
