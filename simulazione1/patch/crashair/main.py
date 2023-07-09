#/usr/bin/env python

from bottle import (
    default_app, run,
    route, get, post, put,
    view, error,
    request, response,
    redirect, abort,
    static_file,
)
# from database import insert_user, get_user, insert_optional, list_optional, list_reservations, insert_reservation
from database import *
from utils import *
from datetime import datetime
from base64 import b64encode

################################################################################

application = app = default_app()

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static/')

@error(400)
@error(401)
@error(404)
@error(500)
@view('error')
def error_handler(error):
    return dict(
        code=error.status,
        message=error.body,
        title='Bad Request'
    )

################################################################################
# LOGIN
################################################################################

@get('/')
@view('homepage')
def homepage():
    username = validate_session(request)
    return {'username': username}

@post('/register')
def user_register():
    username = request.forms.username
    password = request.forms.password

    if not valid_username(username): abort(400, text='Invalid username')
    if not valid_password(password): abort(400, text='Invalid password')

    if not insert_user(username, password):
        abort(400, text='User already exists')
    
    create_session(response, username)
    redirect('/')

@post('/login')
def user_login():
    username = request.forms.username
    password = request.forms.password
    
    if not valid_username(username): abort(400, text='Invalid username')
    if not valid_password(password): abort(400, text='Invalid password')

    if get_user(username, password) is None:
        abort(401, text='Login failed')
    else:
        create_session(response, username)
        redirect('/')


################################################################################
# OPTIONALS
################################################################################

@get('/optionals')
@view('optionals')
def list_optionals():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    return {'username': username, 'optionals':list_optional()}

@get('/optionals/<ID:int>')
@view('optional')
def get_optional(ID):
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    optional = get_single_optional(ID, username)
    if optional is None: abort(401, text='Optional not found.')
    
    edit = optional['owner'] == username
    
    return {'username': username, 'edit':edit, 'op':optional}

@post('/optionals')
def add_optional():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    type = int(request.forms.type)
    instructions = request.forms.instructions
    password = request.forms.password or None

    if password and not valid_password(password): abort(400, text='Invalid password')
    if not valid_instructions(instructions): abort(400, text='Invalid instructions')
        
    if not insert_optional(username, type, instructions, password):
        abort(500, text='Failed to insert new optional')
    redirect('/optionals')

@post('/optionals/<ID:int>')
def set_optional(ID):
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    type = int(request.forms.type)
    instructions = request.forms.instructions
    password = request.forms.password or None

    if password and not valid_password(password): abort(400, text='Invalid password')
    if not valid_instructions(instructions): abort(400, text='Invalid instructions')
        
    if not edit_single_optional(ID, username, type, instructions, password):
        abort(500, text='Failed to update optional')

    redirect('/optionals')
################################################################################
# RESERVATIONS
################################################################################

@get('/reservations')
@view('reservations')
def get_reservations():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    return {'username': username, 'reservations':list_reservations(), 'optionals':list_optional()}

@get('/reservations/<ID:int>')
@view('reservation')
def get_reservation(ID):
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    reservation = get_single_reservation(ID)
    if reservation is None: abort(401, text='Reservation not found.')
    
    edit = reservation['owner'] == username
    
    return {'username': username, 'edit':edit, 'res':reservation, 'optionals':list_optional()}

@post('/reservations')
def add_reservation():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    seat_reservation = bool(request.forms.seat_reservation)
    online_checkin = bool(request.forms.online_checkin)
    optional_id = int(request.forms.optional_id) if request.forms.optional_id else None

    if not insert_reservation(username, seat_reservation, online_checkin, optional_id):
        abort(500, text='Failed to insert new reservation')
    redirect('/reservations')

@post('/reservations/<ID:int>')
def set_reservation(ID):
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    seat_reservation = bool(request.forms.seat_reservation)
    online_checkin = bool(request.forms.online_checkin)
    optional_id = int(request.forms.optional_id) if request.forms.optional_id else None

    if not edit_single_reservation(ID, username, seat_reservation, online_checkin, optional_id):
        abort(500, text='Failed to update reservation')

    redirect('/reservations')

################################################################################
# CHECKOUT
################################################################################

@get('/checkout')
@view('checkout')
def get_checkout():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    if get_user_ticket(username) is not None:
        redirect('/ticket')

    return {'username': username, 'reservations':list_reservations()}


@get('/checkout/<ID:int>')
def checkout_start(ID):
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    if get_user_ticket(username) is not None:
        redirect('/ticket')

    reservation = get_single_reservation(ID)
    if reservation is None: abort(401, text='Reservation not found.')
    
    optional = get_single_optional(reservation['optional'])

    if optional is not None and optional['owner'] != username and optional['password'] is not None:
        # reservation is using a private optional of another user
        set_checkout_state(response, ID, 'check_pwd')
        redirect('/checkout/check_pwd')
    else:
        set_checkout_state(response, ID, 'finalize')
        redirect('/checkout/finalize')

@get('/checkout/check_pwd')
@view('check_pwd')
def checkout_checkpwd_get():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')

    if get_user_ticket(username) is not None:
        redirect('/ticket')

    reservation_id, state = validate_checkout_state(request)
    if state != 'check_pwd': abort(400, text='Checkout procedure failed.')
    
    return {'username': username}

@post('/checkout/check_pwd')
def checkout_checkpwd_post():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')

    if get_user_ticket(username) is not None:
        redirect('/ticket')

    reservation_id, state = validate_checkout_state(request)
    if state != 'check_pwd': abort(400, text='Checkout procedure failed.')
    
    reservation = get_single_reservation(reservation_id)
    if reservation is None: abort(401, text='Reservation not found.')
    optional = get_single_optional(reservation['optional'])

    in_pwd = request.forms.password
    opt_pwd = optional['password']

    if not valid_password(in_pwd): abort(400, text='Invalid password')

    if secure_equals(in_pwd, opt_pwd):
        set_checkout_state(response, reservation_id, 'finalize')
        redirect('/checkout/finalize')
    else:
        # wrong password, retry
        redirect('/checkout/check_pwd')

@get('/checkout/finalize')
def checkout_finalize():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')

    if get_user_ticket(username) is not None:
        redirect('/ticket')

    reservation_id, state = validate_checkout_state(request)

    delete_checkout_state(response)
    if not create_ticket_for_user(username,reservation_id):
        abort(400, text='Checkout procedure failed.')

    redirect('/ticket')

################################################################################
# TICKET
################################################################################

@get('/ticket')
@view('ticket')
def ticket_page():
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    ticket = get_user_ticket(username)
    if ticket is None:
        redirect('/checkout')

    if ticket['ready_ts'] > datetime.now():
        wait_time = (ticket['ready_ts'] - datetime.now()).total_seconds()
        return {'wait': wait_time}
    else:
        reservation = get_single_reservation(ticket['reservations_id'])
        optional = get_single_optional(reservation['optional'])
        filename_enc = b64encode(ticket['ticket_id'].encode()).decode()
        if not ticket['ready']:
            generate_ticket_file(ticket, reservation, optional)
            set_ticket_as_generated(ticket['ticket_id'])

        return {'wait': None, 'ticket':ticket, 'reservation':reservation, 'optional':optional, 'filename_enc':filename_enc}

@get('/ticket/<path>')
def ticket_file(path):
    username = validate_session(request)
    if username is None: abort(401, text='You must authenticate first')
    
    ticket = get_user_ticket(username)
    if ticket is None:
        redirect('/checkout')
    
    if not ticket['ready']:
        redirect('/ticket')

    return get_ticket_file(path)

################################################################################

if __name__ == '__main__':
    # run(host='localhost', port=8000, reloader=True, debug=True)
    run(host='0.0.0.0', port=8000)
