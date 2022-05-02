"""
This file defines the database models
"""

import datetime
from email.policy import default
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'tutor',
    Field('first_name', 'string', requires=IS_NOT_EMPTY()),
    Field('last_name', 'string', requires=IS_NOT_EMPTY()),
    Field('rate', 'string'),
    Field('user_email', default=get_user_email),
    Field('bio', 'text')
)

db.define_table(
    'classes',
    Field('class_name', 'string', requires=IS_NOT_EMPTY()),
    Field('professor', 'string'), #professor they had when taking the class
    Field('user_email', default=get_user_email),
)

#linkes tutors with classes they've taken
db.define_table(
    'class_to_tutor',
    Field('tutor', 'reference tutor'),
    Field('classes', 'reference classes'),
)



db.tutor.user_email.readable = db.tutor.user_email.writable = False
db.classes.user_email.readable = db.classes.user_email.writable = False
db.tutor.id.readable = db.tutor.id.writable = False
db.classes.id.readable = db.classes.id.writable = False
# db.classes.tutor_id.readable = db.classes.tutor_id.writable = False
db.commit()
