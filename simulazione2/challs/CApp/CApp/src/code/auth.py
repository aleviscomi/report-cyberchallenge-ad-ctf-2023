from functools import wraps
from flask import flash, redirect, url_for, session, g
from .helpers import do_query
import uuid
from .exceptions import *
import hashlib


def is_logged():
    return 'username' in session

def logged(func):
    @wraps(func)
    def f(*args, **argv):
        if not is_logged():
            flash('You need to sign-in first to do that')
            return redirect(url_for('frontend.login_page'))

        return func(*args, **argv)
    return f

def not_logged(func):
    @wraps(func)
    def f(*args, **argv):
        if is_logged():
            return redirect(url_for('frontend.index'))
        return func(*args, **argv)
    return f


def register_user(username, password):
    check_user_exists = 'SELECT id FROM users WHERE username = %s'
    if len(do_query(check_user_exists, [username])) > 0:
        return False

    query = 'INSERT INTO users (username,password, uuid) VALUES (%s, %s,%s)'
    user_id = uuid.uuid4()
    password_hash = hashlib.md5(password.encode()).hexdigest()
    try:
        do_query(query, [username, password_hash, user_id], commit=True)
    except:
        return False
    return user_id


def login_user(username, password):
    query = 'SELECT uuid FROM users WHERE username = %s AND password = %s'
    password_hash = hashlib.md5(password.encode()).hexdigest()
    result = do_query(query, [username, password_hash])

    if len(result) < 1:
        raise WrongPassword()
   

    return result[0]['uuid']
