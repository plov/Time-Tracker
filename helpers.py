import csv
import datetime
import subprocess
import urllib
import uuid

from flask import flash, redirect, render_template, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def validate_form(form, fields, template="register.html"):
    for field in fields:
        if not form.get(field):
            flash(f"must provide {field}")
            return render_template(template)
    return None

def warning(message, tamplate = "register.html"):
    flash(message)
    return render_template(tamplate, )