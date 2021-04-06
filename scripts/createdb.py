#!/usr/bin/env python

import sys
import os
import argparse
import phonenumbers
import sqlite3
import csv
# phone,uid,email,first_name,last_name,gender,date_registered,birthday,location,hometown,relationship_status,education_last_year,work,groups,pages,last_update,creation_time

# phone:fbid:firstname:lastname:sex:town:hometown:marital_status:job:reg_date:email:dob
def fixlines(lines):
    for line in lines:
        line = line.replace('12:00:00', '')
        yield line

def createdb(input, output):
    db = sqlite3.connect(output)
    cur = db.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS leak(
        `num` TEXT PRIMARY KEY, 
        `checked` INT DEFAULT 0, 
        `fistname` INT, 
        `lastname` INT, 
        `sex` INT, 
        `town` INT,
        `hometown` INT,
        `marital_status` INT,
        `job` INT,
        `reg_date` INT,
        `email` INT,
        `dob` INT)"""
    )

    with open(input, "r") as f:
        reader = csv.reader(fixlines(f), delimiter=":")

        for line in reader:
            assert len(line) == 12
            
            try:
                parsed = phonenumbers.parse("+{}".format(line[0]))
                num = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )

                def present(s):
                    return len(s.strip()) > 0

                firstname = present(line[2])
                lastname = present(line[3])
                sex = present(line[4])
                town = present(line[5])
                hometown = present(line[6])
                martial_status = present(line[7])
                job = present(line[8])
                reg_date = present(line[9])
                email = present(line[10])
                dob = present(line[11])

                row = (
                    num,
                    firstname,
                    lastname,
                    sex,
                    town,
                    hometown,
                    martial_status,
                    job,
                    reg_date,
                    email,
                    dob,
                )
                print(row)

                print()

                cur.execute(
                    """INSERT INTO leak(`num`, `fistname`, `lastname`, `sex`, `town`, `hometown`, `marital_status`, `job`, `reg_date`, `email`, `dob`)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                    row,
                )
            except phonenumbers.phonenumberutil.NumberParseException:
                pass

        db.commit()
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-i", "--input", required=True)

    args = parser.parse_args()
    createdb(args.input, args.output)
