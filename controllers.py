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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma

url_signer = URLSigner(session)

@action('index',  method = ["GET", "POST"])
@action.uses(db, auth, 'index.html')
def index():
    print("User:", get_user_email())
    form = Form(db.classes, deletable = False ,csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # update happened, redirect
        redirect(URL('index'))
    return dict(form = form)

# need to restrict this to only those who are signed in
@action('tutor_add_class')
@action.uses(db, auth, 'tutor_add_class.html')
def tutor_add_class():
    form = Form(db.class_tutors, deletable = False ,csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # update happened, redirect
        redirect(URL('index'))
    return dict(form = form)