from logging import error
import sqlite3
import time
import os
import phonenumbers
from flask import Flask, Response, g, render_template, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE=os.getenv("APP_DATABASE", "db.sqlite"),
    RATELIMIT_STORAGE_URL=os.getenv("RATELIMIT_STORAGE", "memory://"),
)

limiter = Limiter(app, key_func=get_remote_address, default_limits=["360 per hour"])


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@limiter.limit("100 per day", methods=["POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        phone = request.form.get("phone")
        if not phone:
            return render_template("index.html", error="Invalid phone number")

        cur = get_db().cursor()
        parsed = phonenumbers.parse(phone, "SI")
        formatted = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )
        resp = cur.execute(
            "SELECT `checked`, `fistname`, `lastname`, `sex`, `town`, `hometown`, `marital_status`, `job`, `reg_date`, `email`, `dob` FROM leak WHERE num = ?",
            (formatted,),
        ).fetchone()
        if resp:
            if resp[0] == 0:
                cur.execute(
                    "UPDATE leak SET checked = ? WHERE num = ?",
                    (int(time.time()), formatted),
                )
                get_db().commit()
            found = True

            leaked = {
                "firstname": bool(resp[1]),
                "lastname": bool(resp[2]),
                "sex": bool(resp[3]),
                "town": bool(resp[4]),
                "hometown": bool(resp[5]),
                "marital_status": bool(resp[6]),
                "job": bool(resp[7]),
                "reg_date": bool(resp[8]),
                "email": bool(resp[9]),
                "dob": bool(resp[10]),
            }
        else:
            found = False
            leaked = None
        return render_template(
            "index.html", found=found, phone=formatted, leaked=leaked
        )
    else:
        return render_template("index.html")
