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
from itertools import groupby

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
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *
from py4web.utils.grid import Grid, GridClassStyleBulma

from .models import get_user_email, get_first_name, get_last_name, get_tutor

url_signer = URLSigner(session)


@action("index")
@action.uses("index.html", db, auth, url_signer)
def index():
    classes = {c["id"]: c["class_name"] for c in db(db.classes).select()}
    get_tutors_url = URL("get_tutors", signer=url_signer)
    get_tutor_classes_url = URL("get_tutor_classes", signer=url_signer)

    print(classes)
    return dict(
        get_tutors_url=get_tutors_url,
        get_tutor_classes_url=get_tutor_classes_url,
        classes=classes,
    )


@action("get_tutors")
@action.uses(db, auth)
def get_tutors():
    classes = request.params.get("classes", None)

    q = db.tutors.id == db.tutors.id

    if classes is not None:
        classes = [int(c) for c in classes.split(",")]

        q &= db.tutors.id == db.class_to_tutor.tutor_id
        q &= db.class_to_tutor.class_id.belongs(classes)

    tutor_list = db(q).select(db.tutors.ALL, groupby=db.tutors.id).as_list()

    print(tutor_list)
    return dict(tutor_list=tutor_list)


@action("get_tutor_classes")
@action.uses(url_signer.verify(), db, auth)
def get_tutor_classes():

    tutor_id = int(request.params.get("tutor_id"))
    classes_tutored = db((db.class_to_tutor.tutor_id == tutor_id)).select()

    classes = db(db.classes).select().as_list()

    classes_to_return = []

    class_dictionary = {}
    for c in classes:
        class_dictionary[c["id"]] = c["class_name"]
    for tutor_class in classes_tutored:
        classes_to_return.append(class_dictionary[tutor_class["class_id"]])

    return dict(classes_tutored=classes_to_return)


@action("tutor_home", method=["GET", "POST"])
@action.uses("tutor_home.html", db, auth.user)
def tutor_home():
    if get_tutor() is not None:
        tutor_id = get_tutor().id
    else:
        tutor_id = None
    tutor_classes = (
        db(
            (db.class_to_tutor.tutor_id == tutor_id)
            & (db.class_to_tutor.class_id == db.classes.id)
        )
        .select()
        .as_list()
    )
    if tutor_id is None:
        redirect(URL("create_tutor"))

    return dict(classes=tutor_classes)


@action("delete_class/<class_id:int>")
@action.uses(db, session, auth.user)
def delete(class_id=None):
    assert class_id is not None

    tutor_id = get_tutor().id
    db(
        (db.class_to_tutor.class_id == class_id)
        & (db.class_to_tutor.tutor_id == tutor_id)
    ).delete()
    redirect(URL("tutor_home"))
    return dict()


# create tutor profile (rate, bio)
@action("create_tutor", method=["GET", "POST"])
@action.uses("create_tutor.html", db, auth.user)
def create_tutor():

    form = Form(
        [
            Field("base_rate"),
            Field("bio"),
            Field("major"),
            Field("year"),
            Field("class_history"),
        ],
        deletable=False,
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    if form.accepted:
        db.tutors.update_or_insert(
            user_id=auth.current_user["id"],
            major=form.vars["major"],
            year=form.vars["year"],
            rate=form.vars["base_rate"],
            bio=form.vars["bio"],
            history=form.vars["class_history"],
        )
        redirect(URL("tutor_home"))

    return dict(form=form)


# edit a tutor profile
@action("edit_tutor", method=["GET", "POST"])
@action.uses("edit_tutor.html", db, auth.user)
def create_tutor():
    tutor = get_tutor()

    if tutor is None:
        redirect(URL("index"))

    form = Form(
        db.tutors,
        record=tutor,
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
            Field("class_name", requires=IS_IN_SET(classes)),
            # Field("availability", default = "1 PM - 2 PM"),
        ],
        deletable=False,
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    if form.accepted:
        db.class_to_tutor.insert(
            tutor_id=get_tutor().id, class_id=form.vars["class_name"]
        )
        redirect(URL("tutor_home"))

    return dict(form=form)


@action("back")
@action.uses(db, auth.user, url_signer)
def back():
    redirect(URL("index"))
    return dict()

@action('aboutus')
@action.uses('aboutus.html')
def aboutus():
    return dict()
