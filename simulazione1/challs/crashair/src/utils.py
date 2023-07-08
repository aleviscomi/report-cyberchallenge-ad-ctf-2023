
import secrets
import logging
import json
import re
from time import time
from database import get_user
from base64 import b64decode, b64encode

COOKIES_SIGN_SECRET = secrets.token_urlsafe(16)
SESSION_DURATION = 12

def valid_username(username):
    return re.match(r'[-_a-zA-Z0-9]{1,30}', username) is not None

def valid_password(password):
    return len(password) <= 50

def valid_instructions(instructions):
    return len(instructions) <= 200

def create_session(response, username):
    token = (int(time()), username)
    response.set_cookie('session', token, secret=COOKIES_SIGN_SECRET)

def validate_session(request):
    try:
        session_cookie = request.get_cookie('session', secret=COOKIES_SIGN_SECRET)
        if session_cookie is None:
            logging.warning('Session cookie absent or tampered')
            return None

        ts, username = session_cookie

        if type(ts) != int or type(username) != str:
            logging.warning('Session cookie had unexpected type')
            return None

        if ts < time() - SESSION_DURATION*60:
            # session is too old
            logging.warning('Session cookie was too old')
            return None
        
        if get_user(username) is None:
            return None

        return username

    except:
        logging.warning('Unexpected error in session cookie')
        return False

def set_checkout_state(response, reservation_id, state):
    token = (int(time()), reservation_id, state)
    response.set_cookie('checkout', token, secret=COOKIES_SIGN_SECRET)

def delete_checkout_state(response):
    response.set_cookie('checkout', '', expires=0)

def validate_checkout_state(request):
    try:
        checkout_cookie = request.get_cookie('checkout', secret=COOKIES_SIGN_SECRET)
        if checkout_cookie is None:
            logging.warning('Checkout cookie absent or tampered')
            return None

        ts, reservation_id, state = checkout_cookie

        if type(ts) != int or type(reservation_id) != int or type(state) != str:
            logging.warning('Checkout cookie had unexpected type')
            return None

        if ts < time() - 2*60:
            logging.warning('Checkout cookie was too old')
            return None

        return reservation_id, state

    except:
        logging.warning('Unexpected error in checkout cookie')
        return False

def secure_equals(s1,s2):
    # compare the strings in constant time to avoid time based attacks
    # explained in https://security.stackexchange.com/questions/83660/simple-string-comparisons-not-secure-against-timing-attacks
    ris = 0
    for c1,c2 in zip(s1,s2):
        ris |= ord(c1) ^ ord(c2)
    return ris == 0

def generate_ticket_file(ticket, reservation, optional):
    path = 'tickets/' + ticket['ticket_id']
    with open(path, 'w') as f:
        ris = {
            'ticket_ID': ticket['ticket_id'],
            'passenger': ticket['user_id'],
            'seat_reservation': reservation['seat'],
            'online_checkin': reservation['checkin'],
            'purchase_date': str(ticket['ts']),
            'optional': None,
        }
        if optional is not None:
            ris['optional'] = {
                'type': optional['type'],
                'instructions': optional['instructions'],
                'private': optional['password'] is not None,
            }
        json.dump(ris, f, indent=4)

def get_ticket_file(filename):
    if '../' in filename: return None
    filename = b64decode(filename).decode()

    with open('tickets/' + filename, 'rb') as f:
        return f.read()
