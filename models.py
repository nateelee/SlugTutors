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
    'classes',
    Field('class_name')
)

db.define_table(
    'class_tutors',
    Field('tutor_name'),
    Field('class_id', 'reference classes'),
    Field('rate'),
    Field('bio'),
    Field('contact'),
    Field('email')
)
db.class_tutors.id.readable = db.class_tutors.id.writable = False
db.classes.id.readable = db.classes.id.writable = False

db.commit()
