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

from collections import OrderedDict

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
)
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *

from .models import get_user_email, get_first_name, get_last_name

url_signer = URLSigner(session)


@action("index")
@action.uses("index.html", db, auth)
def index():
    return {}


@action("tutor_home", method=["GET", "POST"])
@action.uses("tutor_home.html", db, auth.user)
def tutor_home():
    tutor = db(db.tutors.user == auth.current_user["id"]).select().first()
    if tutor is None:
        redirect(URL("create_tutor"))

 

    return dict(rows=rows, tutor_id=tutor_id)


@action("delete/<class_id:int>")
@action.uses(db, session, auth.user)
def delete(class_id=None):
    assert class_id is not None

    db(db.class_to_tutor.class_id == class_id).delete()
    redirect(URL("tutor_home"))
    return dict()


# create tutor profile (rate, bio)
@action("create_tutor", method=["GET", "POST"])
@action.uses("create_tutor.html", db, auth.user)
def create_tutor():

    form = Form(
        [Field("base_rate"), Field("bio")],
        deletable=False,
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    if form.accepted:
        db.tutors.update_or_insert(
            user=auth.current_user["id"],
            rate=form.vars["base_rate"],
            bio=form.vars["bio"],
        )
        redirect(URL("tutor_home"))

    return dict(form=form)


# edit a tutor profile
@action("edit_tutor", method=["GET", "POST"])
@action.uses("edit_tutor.html", db, auth.user)
def create_tutor():
    record = db(db.tutors.user == auth.current_user["id"]).select().first()

    if record is None:
        redirect(URL("index"))

    form = Form(
        db.tutors,
        record=record,
        deletable=False,
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    if form.accepted:
        redirect(URL("tutor_home"))

    return dict(form=form)


# need to restrict this to only those who are signed in
@action("tutor_add_class", method=["GET", "POST"])
@action.uses("tutor_add_class.html", db, auth.user)
def tutor_add_class():
    classes = {c["id"]: c["class_name"] for c in db(db.classes).select()}

    form = Form(
        [
            Field("class_id", requires=IS_IN_SET(classes)),
        ],
        deletable=False,
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    if form.accepted:
        db.class_to_tutor.insert(
            tutor=auth.current_user["id"], class_id=form.vars["class_id"]
        )
        redirect(URL("tutor_home"))

    return dict(form=form)
