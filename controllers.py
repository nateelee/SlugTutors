"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *

url_signer = URLSigner(session)

@action('index',  method = ["GET", "POST"])
@action.uses(db, auth, 'index.html')
def index():
    # print("User:", get_user_email())
    form = Form(db.classes, deletable = False ,csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # update happened, redirect
        redirect(URL('index'))
    return dict(form = form)

dummyemail = "raghav@gmail.com"

@action('tutorHomePage',  method = ["GET", "POST"])
@action.uses(db, auth.user, 'tutorHomePage.html')
def tutorHomePage():
    # form = Form(db.classes, deletable = False ,csrf_session=session, formstyle=FormStyleBulma)
    # if form.accepted:
    #     # update happened, redirect
    #     redirect(URL('tutorHomePage'))
    # return dict(form = form)
    # rows = db(db.classes.email == get_user_email()).select()
    # return()
    rows = db(
        db.class_tutors.email == dummyemail).select()
        # db.class_tutors.class_id == db.classes.id).select()
    return dict(rows = rows)

# need to restrict this to only those who are signed in
@action('tutor_add_class', method = ["GET", "POST"])
@action.uses(db, auth, 'tutor_add_class.html')
def tutor_add_class():
    query = db(db.classes).select().as_list()
    
    class_set = []
    class_id = {}
    for table in query:
        class_set.append(table['class_name'])
        class_id[table['class_name']] = table['id']
    form = Form(
        [Field('tutor_name'),
        Field('class_name', requires=IS_IN_SET(class_set)),
        Field('rate'),
        Field('bio'),
        Field('contact'),
        Field('email')],
        deletable = False ,csrf_session=session, formstyle=FormStyleBulma
    )
    if form.accepted:
        # update happened, redirect
        db.class_tutors.insert(
            tutor_name = form.vars['tutor_name'],
            class_id = class_id[form.vars['class_name']],
            rate = form.vars['rate'],
            bio = form.vars['bio'],
            contact = form.vars['contact'],
            email = form.vars['email'] 
        )
        redirect(URL('tutorHomePage'))
    return dict(form = form)


# @action('delete_tutorClass/<tutor_id:int>')
# @action.uses(db, session, auth.user, url_signer)
# def delete(tutor_id=None):
#     assert tutor_id is not None
#     # db(db.class.id == tutor_id).delete()
#     redirect(URL('tutorHomePage'))
