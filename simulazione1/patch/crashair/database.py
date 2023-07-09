import sqlite3
import secrets
import pathlib
from datetime import datetime, timedelta

DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    query_users = (
        'CREATE TABLE IF NOT EXISTS users ('
        'user_id            TEXT        NOT NULL PRIMARY KEY,'
        'password           TEXT        NOT NULL,'
        'ts                 TIMESTAMP   NOT NULL'
        ')'
    )

    query_optionals = (
        'CREATE TABLE IF NOT EXISTS optionals ('
        'optional_id        INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,'
        'owner_id           TEXT        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,'
        'type               INTEGER     NOT NULL,'
        'instructions       TEXT        NOT NULL,'
        'password           TEXT,'
        'ts                 TIMESTAMP   NOT NULL'
        ')'
    )

    query_reservation = (
        'CREATE TABLE IF NOT EXISTS reservations ('
        'reservations_id    INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,'
        'owner_id           TEXT        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,'
        'optional_id        INTEGER     REFERENCES optionals(optional_id) ON DELETE SET NULL,'
        'seat_reservation   INTEGER     NOT NULL,'
        'online_checkin     INTEGER     NOT NULL,'
        'ts                 TIMESTAMP   NOT NULL'
        ')'
    )

    query_tickets = (
        'CREATE TABLE IF NOT EXISTS tickets ('
        'ticket_id          TEXT        NOT NULL PRIMARY KEY,'
        'user_id            TEXT        NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,'
        'reservations_id    INTEGER     NOT NULL REFERENCES reservations(reservations_id) ON DELETE CASCADE,'
        'ready              INTEGER     NOT NULL,'
        'ready_ts           TIMESTAMP   NOT NULL,'
        'ts                 TIMESTAMP   NOT NULL'
        ')'
    )

    conn = get_db_connection()
    with conn:
        conn.execute(query_users)
        conn.execute(query_optionals)
        conn.execute(query_reservation)
        conn.execute(query_tickets)
    conn.close()

    # create ticket dir if absent
    pathlib.Path('./tickets/').mkdir(exist_ok=True)

################################################################################
# USERS
################################################################################

USER_TTL = 12

def clean_old_users(minutes=USER_TTL):
    timestamp = datetime.now() - timedelta(minutes=minutes)

    conn = get_db_connection()
    with conn:
        conn.execute('DELETE FROM users WHERE ts < ?', (timestamp,))
    conn.close()

def insert_user(user_id, password):
    clean_old_users()

    timestamp = datetime.now()

    success = False
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('INSERT INTO users(user_id, password, ts) VALUES (?,?,?)', (user_id, password, timestamp))
        success = True
    except sqlite3.IntegrityError:
        # user_id already present
        success = False
    conn.close()

    return success

def get_user(user_id, password=None):
    clean_old_users()
    conn = get_db_connection()

    query = 'SELECT * FROM users WHERE user_id = ?'
    if password is not None:
        query += 'AND password = ?'
        with conn:
            ris = conn.execute(query, (user_id, password)).fetchone()
        conn.close()
        return ris

    with conn:
        ris = conn.execute(query, (user_id,)).fetchone()
    conn.close()
    return ris

################################################################################
# OPTIONALS
################################################################################

OPTIONAL_TYPE = {
    1:'Custom-made dessert',
    2:'On-demand movie',
}
def list_optional():
    conn = get_db_connection()
    with conn:
        optionals = conn.execute('SELECT * FROM optionals ORDER BY ts DESC').fetchall()
    conn.close()

    # process optional
    ris = list()
    for op in optionals:
        ID, owner, type, instructions, password, ts = op
        ris.append({
            'ID': ID,
            'owner': owner,
            'type': OPTIONAL_TYPE.get(type, 'Other...'),
            'instructions': instructions,
            'password': password,
            'ts': ts,
        })
    return ris

def get_single_optional(ID, username=None):
    if ID is None: return None

    
    conn = get_db_connection()
    with conn:
        optional = conn.execute('SELECT * FROM optionals WHERE optional_id = ?', (ID,)).fetchone()
    conn.close()
    if optional is None:
        return None
    
    _, owner, type, instructions, password, ts = optional

    if username is not None and owner != username:
        return None

    return {
        'ID': ID,
        'owner': owner,
        'type': OPTIONAL_TYPE.get(type, 'Other...'),
        'instructions': instructions,
        'password': password,
        'ts': ts,
    }

def edit_single_optional(optional_id, owner_id, type, instructions, password):
    timestamp = datetime.now()

    success = False
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('''
            UPDATE optionals
            SET type = ?,
            instructions = ?,
            password = ?,
            ts = ?
            WHERE optional_id = ? AND owner_id = ?''', (type, instructions, password, timestamp, optional_id, owner_id))
        success = True
    except sqlite3.IntegrityError as e:
        success = False
    conn.close()

    return success

def insert_optional(owner_id, type, instructions, password):
    timestamp = datetime.now()

    success = False
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('INSERT INTO optionals(owner_id, type, instructions, password, ts) VALUES (?,?,?,?,?)', (owner_id, type, instructions, password, timestamp))
        success = True
    except sqlite3.IntegrityError as e:
        success = False
    conn.close()

    return success

################################################################################
# RESERVATIONS
################################################################################

def list_reservations():
    conn = get_db_connection()
    with conn:
        reservations = conn.execute('SELECT * FROM reservations ORDER BY ts DESC').fetchall()
    conn.close()

    # process reservations
    ris = list()
    for re in reservations:
        ID, owner, optional, seat, checkin, ts = re
        ris.append({
            'ID': ID,
            'owner': owner,
            'optional': optional,
            'seat': bool(seat),
            'checkin': bool(checkin),
            'ts': ts,
        })
    return ris

def get_single_reservation(ID):
    conn = get_db_connection()
    with conn:
        reservation = conn.execute('SELECT * FROM reservations WHERE reservations_id = ?', (ID,)).fetchone()
    conn.close()
    if reservation is None:
        return None
    
    _, owner, optional, seat, checkin, ts = reservation
    return {
        'ID': ID,
        'owner': owner,
        'optional': optional,
        'seat': bool(seat),
        'checkin': bool(checkin),
        'ts': ts,
    }

def edit_single_reservation(reservations_id, owner_id, seat_reservation, online_checkin, optional_id):
    timestamp = datetime.now()

    success = False
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('''
            UPDATE reservations
            SET seat_reservation = ?,
            online_checkin = ?,
            optional_id = ?,
            ts = ?
            WHERE reservations_id = ? AND owner_id = ?''', (seat_reservation, online_checkin, optional_id, timestamp, reservations_id, owner_id))
        success = True
    except sqlite3.IntegrityError as e:
        success = False
    conn.close()

    return success

def insert_reservation(owner_id, seat_reservation, online_checkin, optional_id):
    timestamp = datetime.now()

    success = False
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('INSERT INTO reservations(owner_id, seat_reservation, online_checkin, optional_id, ts) VALUES (?,?,?,?,?)', (owner_id, seat_reservation, online_checkin, optional_id, timestamp))
        success = True
    except sqlite3.IntegrityError as e:
        success = False
    conn.close()

    return success


################################################################################
# TICKETS
################################################################################

def create_ticket_for_user(username, reservations_id):
    ticket_id = secrets.token_urlsafe(15)
    timestamp = datetime.now()
    ready_ts = timestamp + timedelta(seconds=1.5)
    ready = 0

    success = False
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('INSERT INTO tickets(ticket_id, user_id, reservations_id, ready, ready_ts, ts) VALUES (?,?,?,?,?,?)', (ticket_id, username, reservations_id, ready, ready_ts, timestamp))
        success = True
    except sqlite3.IntegrityError as e:
        success = False
    conn.close()

    return success

def set_ticket_as_generated(ticket_id):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('UPDATE tickets SET ready = 1 WHERE ticket_id = ?', (ticket_id,))
        success = True
    except sqlite3.IntegrityError as e:
        success = False
    conn.close()


def get_user_ticket(user_id):
    conn = get_db_connection()
    with conn:
        # ris = conn.execute('SELECT ticket FROM users WHERE user_id = ?', (user_id,)).fetchone()
        ris = conn.execute('''
            SELECT ticket_id, user_id, reservations_id, ready, ready_ts, ts
            FROM tickets 
            WHERE user_id = ?''', (user_id,)).fetchone()
    conn.close()
    if ris is None: return None

    ticket_id, user_id, reservations_id, ready, ready_ts, ts = ris
    return {
        'ticket_id':ticket_id,
        'user_id':user_id,
        'reservations_id':reservations_id,
        'ready':bool(ready),
        'ready_ts':ready_ts,
        'ts':ts,
    }

################################################################################
# INIT
################################################################################

# init db if non existant
init_db()
