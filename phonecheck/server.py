from logging import error
import sqlite3
import time
import os
import phonenumbers
from flask import Flask, g, render_template, request
from flask_limiter import Limiter

app = Flask(__name__)

app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE=os.getenv("APP_DATABASE", "db.sqlite"),
    RATELIMIT_STORAGE_URL=os.getenv("RATELIMIT_STORAGE", "memory://"),
)


def get_ipaddr():
    if request.access_route:
        return request.access_route[0]
    else:
        return request.remote_addr or "127.0.0.1"


limiter = Limiter(app, key_func=get_ipaddr, default_limits=["360 per hour"])


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
            return render_template("index.html", error="Neveljaven vnos")

        try:
            cur = get_db().cursor()
            parsed = phonenumbers.parse(phone, "SI")
            if parsed.country_code != 386:
                return render_template("index.html", error="Iskanje deluje le za slovenske številke (+386)")

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
        except phonenumbers.phonenumberutil.NumberParseException:
            return render_template("index.html", error="Neveljaven vnos")
    else:
        return render_template("index.html")
