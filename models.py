"""
This file defines the database models
"""

import datetime
import json
import os
from .common import db, Field, auth
from .settings import APP_FOLDER
from pydal.validators import *


def get_tutor():
    return (
        db(db.tutors.user_id == auth.current_user["id"]).select().first()
        if auth.current_user
        else None
    )


def get_user_email():
    return auth.current_user.get("email") if auth.current_user else None


def get_first_name():
    return auth.current_user.get("first_name") if auth.current_user else None


def get_last_name():
    return auth.current_user.get("last_name") if auth.current_user else None

def get_full_name():
    return f"{auth.current_user.get('first_name')} {auth.current_user.get('last_name')}" if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()

def get_user():
    return auth.current_user.get('id') if auth.current_user else None


db.define_table(
    "tutors",
    Field(
        "user_id", "reference auth_user", writable=False, readable=False
    ),
    Field("name", default = get_full_name),
    Field("email", default = get_user_email),
    Field("rate", "string", label="Base Rate"),
    Field("bio", "text", requires=IS_NOT_EMPTY()),
    Field("major", requires=IS_NOT_EMPTY()),
    Field("year", requires=IS_NOT_EMPTY()),
    Field("Monday"),
    Field("Tuesday"),
    Field("Wednesday"),
    Field("Thursday"),
    Field("Friday"),
    Field("Saturday"),
    Field("Sunday"),
)

db.define_table(
    "history",
    Field("tutor_id", "reference tutors"),
    Field("coarse_name", requires=IS_NOT_EMPTY(), label="Class Name"),
    Field("instructor", requires=IS_NOT_EMPTY()),
    Field("quarter_taken", requires=IS_NOT_EMPTY()),
)

db.define_table('post',
                Field('name'),
                Field('post_body'),
                Field('tutor_being_rated'),
                Field('rating_number', 'integer', default = 0)
                )

db.define_table('thumb',
                Field('post', 'reference post'),
                Field('rating', 'integer', default=0),
                Field('rater_name'),
                Field('rater_id', 'reference auth_user', default=get_user) # User doing the rating.
                )

db.define_table(
    "classes",
    Field("class_name", "string", requires=IS_NOT_EMPTY()),
)

# linkes tutors with classes they've taken
db.define_table(
    "class_to_tutor",
    Field("tutor_id", "reference tutors"),
    Field("class_id", "reference classes"),
    Field("availability", default = "None"),
)

db.define_table(
    "days",
    Field("Monday"),
    Field("Tues"),
    
)

db.tutors.id.readable = False
db.tutors.id.writable = False
db.tutors.email.writable = False
db.classes.id.readable = False
db.classes.id.writable = False
db.history.id.readable = False
db.history.id.writable = False

CLASSES = os.path.join(APP_FOLDER, "data", "classes.json")

for c in json.load(open(CLASSES)):
    if not db(db.classes.class_name == c).select().first():
        db.classes.insert(class_name=c)

db.commit()
