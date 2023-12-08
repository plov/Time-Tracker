from flask import Flask

from dbHelper import dbHelper
app = Flask(__name__)


db = dbHelper("TT.db")


@app.route("/")
def home():
    users = db.execute("select * from users;")

    #for user in users:
    #app.logger.info("user:", users)

    return users