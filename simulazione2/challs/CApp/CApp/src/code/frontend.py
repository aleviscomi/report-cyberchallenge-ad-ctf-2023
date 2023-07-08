from flask import Blueprint, jsonify, request, render_template, url_for
from .exceptions import *
from .wm import WM
from .auth import *


frontend = Blueprint('frontend', 'frontend')


@frontend.get('/')
def index():
    return render_template('index.html')

@frontend.get('/terminal')
@logged
def terminal():
    return render_template('terminal.html')

@frontend.post('/command')
@logged
def command():
    codeline = request.json.get('command', '')
    if len(codeline) > 1000:
        return jsonify({'output': 'Command too big'})
    wm = WM(session['username'])
    output_lines = [wm.execute_statement(line) for line in codeline.split(';') ]
    output_lines = [str(o) for o in output_lines if o]
    output = '\n\r'.join(output_lines)
    
    wm.save_vm_status()
    return jsonify({'output': output})

@frontend.get('/login')
@not_logged
def login_page():
    return render_template('login.html')

@frontend.post('/login')
@not_logged
def login():
    username = request.form.get('username', False)
    password = request.form.get('password', False)

    if not all((username, password)):
        flash('You need to provide an username, a password')
        return redirect(url_for('frontend.register'))

    try:
        user_id = login_user(username, password)
    except WrongPassword:
        flash('Wrong username or password')
        return redirect(url_for('frontend.login'))

    session['username'] = username
    session['user_id'] = user_id


    flash('Success')
    return redirect(url_for('frontend.index'))

@frontend.get('/register')
@not_logged
def register_page():
    return render_template('register.html')

@frontend.post('/register')
@not_logged
def register():
    username = request.form.get('username', False).replace('\'','').replace('\\','')
    password = request.form.get('password', False)
    
    if not all((username, password)):
        flash('You need to provide an username, a password')
        return redirect(url_for('frontend.register'))

    user_id = register_user(username, password)
    if not user_id:
        flash('User already registered')
        return redirect(url_for('frontend.register'))
    
    session['username'] = username
    session['user_id'] = user_id
    return redirect(url_for('frontend.index'))

@frontend.get('/logout')
@logged
def logout():
    del session['username']
    return redirect(url_for('frontend.index')) 