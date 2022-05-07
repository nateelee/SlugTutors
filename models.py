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
    'class_tutors',
    Field('tutor_name', 'string', requires=IS_NOT_EMPTY()),
    Field('rate', 'string'),
    Field('contact'),
    Field('email', default=get_user_email),
    Field('bio', 'text')
)

db.define_table(
    'classes',
    Field('class_name', 'string', requires=IS_NOT_EMPTY()),
    Field('professor', 'string'), #professor they had when taking the class
    Field('email', default=get_user_email),
)

#linkes tutors with classes they've taken
db.define_table(
    'class_to_tutor',
    Field('class_tutors', 'reference class_tutors'),
    Field('classes', 'reference classes'),
)



db.class_tutors.email.readable = db.class_tutors.email.writable = False
db.classes.email.readable = db.classes.email.writable = False
db.class_tutors.id.readable = db.class_tutors.id.writable = False
db.classes.id.readable = db.classes.id.writable = False

db.commit()
