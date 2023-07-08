from flask import flash, session, g, flash
from functools import wraps
from flask.helpers import url_for
import secrets
from werkzeug.utils import redirect
import hashlib

def flash_form_error(form):
    for _, errors in form.errors.items():
        for error in errors:
            flash(error, category="danger")


# Auth Decorator
def auth(func):
    @wraps(func)
    def f(*args, **argv):
        if not g.logged:
            flash('You need to be logged to do that', category='danger')
            return redirect(url_for('register'))
        
        return func(*args, **argv)
    return f

# Decorator for login/register
def not_auth(func):
    @wraps(func)
    def f(*args, **argv):
       
        if g.logged:
            return redirect(url_for('index'))

        return func(*args, **argv)
    return f

# Flag generation
def gen_flag(teamname, service, realflag):
    flag_son = hashlib.md5(f'{teamname}.{service}.{realflag}'.encode()).hexdigest()
    return f'FKE{{{flag_son}}}'