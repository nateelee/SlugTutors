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

from .models import get_user_email, get_first_name, get_last_name

url_signer = URLSigner(session)


from .settings import APP_FOLDER
import os
import json
JSON_FILE = os.path.join(APP_FOLDER, "data", "classes.json")
file_read = False

@action('index',  method = ["GET", "POST"])
@action.uses('index.html', db, auth)
def index():
    # during final build, remove this db insertion
    global file_read
    if not file_read:
        f = open(JSON_FILE)
        
        # returns JSON object as
        # a dictionary
        data = json.load(f)
        keys = []
        for mp in data:
            for key,value in mp.items():
                
                db.classes.insert(
                    class_name = value
                )
        file_read = True
    tutor = db(db.tutors.user_email == get_user_email()).select()
    classes = db(db.tutors.user_email == get_user_email()).select()
    return dict(
        tutor = tutor,
        classes = classes
    )
    

@action('tutorHomePage',  method = ["GET", "POST"])
@action.uses('tutorHomePage.html', db, auth.user)
def tutorHomePage():
    res = db.tutors.update_or_insert (
        (db.tutors.user_email == get_user_email()),
        first_name = get_first_name(),
        last_name = get_last_name(),
        rate = "temp rate",
        user_email = get_user_email(),
        bio = "temp bio"
    )
  
    tutor_id = db(db.tutors.user_email == get_user_email()).select()[0].id
    rows = db((db.classes.id == db.class_to_tutor.class_id) & (db.tutors.id == db.class_to_tutor.tutor)).select().as_list()
   
    
    return dict(rows = rows, tutor_id = tutor_id)

@action('delete/<class_id:int>')
@action.uses(db, session, auth.user)
def delete(class_id=None):
    assert class_id is not None

    db(db.class_to_tutor.class_id == class_id).delete()
    redirect(URL('tutorHomePage'))
    return dict()

# extend this to the sign on page /edit profile
@action('create_tutor', method = ["GET", "POST"])
@action.uses('create_tutor.html', db, auth.user)
def create_tutor():
    rows = db(db.tutors.user_email == get_user_email()).select().as_list()
    # print("R0: ", rows[0])
    test = 0
    if rows:
        form = Form(
            [Field('first_name'), Field('last_name'), Field('rate'), Field('bio')],
            record = rows[0],
            deletable = False,
            csrf_session=session, 
            formstyle=FormStyleBulma
        )
        test = 1
    else:
        form = Form(
            [Field('first_name'), Field('last_name'), Field('rate'), Field('bio')],
            deletable = False,
            csrf_session=session, 
            formstyle=FormStyleBulma
        )
    
    if form.accepted:
        # update happened, redirect
        # tutor_id = db(db.tutors.user_email == get_user_email()).select()[0].id
        # print(db(db.tutors.user_email).select())
        if test == 0:
            db.tutors.insert(
                first_name = form.vars['first_name'],
                last_name = form.vars['last_name'],
                rate = form.vars['rate'],
                bio = form.vars['bio']
            )
        else:
            # print(rows[0]['id'])
            row = db((db.tutors.user_email == get_user_email()) & (db.tutors.id == rows[0]['id'])).select().first()
            # row = db()
            row.update_record(
                first_name = form.vars['first_name'],
                last_name = form.vars['last_name'],
                rate = form.vars['rate'],
                bio = form.vars['bio']
            )
        # print("R1: ", row)
        redirect(URL('tutorHomePage'))
    return dict(form = form)

# need to restrict this to only those who are signed in
@action('tutor_add_class/<tutor_id:int>', method = ["GET", "POST"])
@action.uses('tutor_add_class.html', db, auth)
def tutor_add_class(tutor_id = None):
    assert tutor_id is not None
    
    query = db(db.classes).select().as_list()
    
    class_set = []
    class_id = {}
    for table in query:
        query2 = db((db.class_to_tutor.class_id == table['id']) & (db.class_to_tutor.tutor == tutor_id)).select().as_list()
        # print("Q2: ", query2)
        if not query2:
            class_set.append(table['class_name'])
            class_id[table['class_name']] = table['id']

    form = Form(
        [
            Field('class_name', requires=IS_IN_SET(class_set)),
        ], 
        deletable = False,
        csrf_session=session, 
        formstyle=FormStyleBulma
    )
    
    if form.accepted:
        # update happened, redirect
      
        db.class_to_tutor.insert(
            tutor = tutor_id,
            class_id = class_id[form.vars['class_name']]
        )
        redirect(URL('tutorHomePage'))
    return dict(form = form)