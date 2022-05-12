"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
db.define_table(
    'tutors',
    Field('user_id', 'reference auth_user'), # Reference to rest of the profile. 
    Field('rate', 'string'),
    Field('bio', 'text')
)
# No I would remove this table. 

db.define_table(
    'classes',
    Field('class_name', 'string', requires=IS_NOT_EMPTY()),
    # Field('professor', 'string'), #professor they had when taking the class
    # Field('user_email', default=get_user_email),
)

#linkes tutors with classes they've taken
db.define_table(
    'class_to_tutor',
    Field('tutor', 'reference tutors'), 
    Field('tutor', 'reference auth_user'), # if you put all info together, in which case 
            # you need to validate that the user who is a tutor has a is_tutor=True. 
    Field('class_id', 'reference classes'),
)

db.define_table(
    'contact',
    Field('tutor_id', 'reference tutor'),
    Field('student_id', 'reference auth_user'),
    Field('class_id', 'reference class'),
)

db.define_table(
    'messages',
    Field('contact_id', 'reference contact'),
    Field('sender', 'reference auth_user'),
    Field('send_on', 'datetime', default=get_time),
    Field('message', 'text'),
)


db.tutors.user_email.readable = db.tutors.user_email.writable = False
# db.classes.user_email.readable = db.classes.user_email.writable = False
db.tutors.id.readable = db.tutors.id.writable = False
db.classes.id.writable = False
# db.classes.tutor_id.readable = db.classes.tutor_id.writable = False
db.commit()