"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

# def get_user_firstname():
#     return auth.current_user.get('first_name') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
db.define_table(
    'tutors',
    Field('first_name', 'string', requires=IS_NOT_EMPTY()),
    Field('last_name', 'string', requires=IS_NOT_EMPTY()),
    Field('rate', 'string'),
    Field('user_email', default=get_user_email),
    Field('bio', 'text')
)

db.define_table(
    'classes',
    Field('class_name', 'string', requires=IS_NOT_EMPTY()),
)

#linkes tutors with classes they've taken
db.define_table(
    'class_to_tutor',
    Field('tutor', 'reference tutors'),
    Field('class_id', 'reference classes'),
)



db.tutors.user_email.readable = db.tutors.user_email.writable = False
# db.classes.user_email.readable = db.classes.user_email.writable = False
db.tutors.id.readable = db.tutors.id.writable = False
db.classes.id.writable = False
# db.classes.tutor_id.readable = db.classes.tutor_id.writable = False
db.commit()