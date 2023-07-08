import sys
import os
from flask import Flask, redirect, url_for, render_template, g, session, flash
from flask import request, jsonify
import sqlalchemy
from forms import LoginForm, RegisterForm, FlagForm, ServiceForm
from models import Service, Team, db, Tick
from utils import *
from flask_bootstrap import Bootstrap
import jwt
import secrets

app = Flask(__name__, static_folder='templates/attachment')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '123456789')
DBHOST = os.environ.get('DBHOST', 'database')
DBUSER = os.environ.get('DBUSER', 'root')
DBPASS = os.environ.get('DBPASS', '')
DBSCHEMA = os.environ.get('DBSCHEMA', 'ctfe')

DB_URI = f'mysql+pymysql://{DBUSER}:{DBPASS}@{DBHOST}/{DBSCHEMA}'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

##############################################
# DO NOT TOUCH THIS, REQUIRED BY THE CHECKER #
app.config['CHECKER_PUBLICK_KEY'] = '''-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEpEnL0LfYkq3G5ZSAMcbhrHed1OJT
JAhqHoAF4Ud+M7mZ4BhkXjQmrjcXWUDewNEkCVlgacIRmvYMY7kM//06ww==
-----END PUBLIC KEY-----
'''
# DO NOT TOUCH THIS, REQUIRED BY THE CHECKER #
##############################################

db.init_app(app)
boostrap = Bootstrap(app)


@app.before_request
def check_user():
    current_tick = Tick.query.order_by(Tick.id.desc()).first()
    if current_tick:
        g.tick = current_tick.id
    else:
        g.tick = 0
    g.logged = False
    if 'user' not in session:
        return

    team_name = session['user']
    user = Team.query.get(team_name)
    if user:
        g.user = user
        g.logged = True
    else:
        del session['user']

@app.get('/')
def index():
    ticks = Tick.query.filter(Tick.running == True).all()
    return render_template('index.html', running_ticks = ticks)

@app.route('/register', methods=['GET', 'POST'])
@not_auth
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        team_name = form.team_name.data
        password = form.password.data

        team = Team(team_name, password)
        db.session.add(team)
        db.session.commit()
        
        session['user'] = team_name
        flash('The registration was successful!')
        return redirect(url_for('index'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
@not_auth
def login():
    form = LoginForm()

    if form.validate_on_submit():
        session['user'] = form.team_name.data
        flash('The login was successful!', category='success')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
@auth
def logout():
    del session['user']
    flash('Signed out', category='success')
    return redirect(url_for('index'))


@app.route('/attack', methods=['GET', 'POST'])
@auth
def attack():
    form = ServiceForm()

    if form.validate_on_submit():
        tick = Tick.query.get(form.tick.data)
        service = int(form.service.data)
        team = form.team.data
        tick_flag = tick.flagstore_1 if service == 1 else tick.flagstore_2

        if not tick_flag:
            tick_flag = 'False_flag'
            form.tick.errors += [f'Warning: Flag for service {service} of tick {tick} not in db. Please note that you won\'t get any real flags']

        flag = gen_flag(team, service, tick_flag)
        access_token = secrets.token_hex(16)
        service = Service(access_token, flag,service)
        service.tick = tick.id
        db.session.add(service)
        db.session.commit()
        host = request.headers['Host']
        if ':' in host:
            host = host.split(':')[0]
        return render_template('service.html', form=form, service=service, host=host)
    
    return render_template('service.html', form=form)


@app.get('/scoreboard')
def scoreboard():
    # Only shows the top 50
    teams = Team.query.order_by(Team.points.desc()).limit(40).all()
    return render_template('scoreboard.html', teams=teams)

@app.get('/challenges')
def challenges():
    return render_template('challenges.html')

@app.get('/training')
def training():
    return render_template('training.html')


@app.route('/submit', methods=['GET', 'POST'])
@auth
def submit():
    form = FlagForm()
    
    if form.validate_on_submit():
        flag = form.flag.data
        team_flag = form.team.data
        service = int(form.service.data)
        
        # Retrieve every running ticks
        ticks = Tick.query.filter(Tick.running == True).all()
        
        real_flags = {}
        for t in ticks:
            real_flag = t.flagstore_1 if service == 1 else t.flagstore_2
            if not real_flag:
                continue
            real_flags[gen_flag(team_flag, service, real_flag)] = real_flag

        print(real_flags, file=sys.stderr)
        if flag in real_flags.keys() and team_flag != g.user.team_name:
            team = Team.query.get(team_flag)
            team.points -= 1
            g.user.points += 1
            db.session.add(g.user)
            db.session.commit()
            
            flash(f'Congratz! here your flag and some points: {real_flags[flag]}', category='success')
            #if assoc.team == 
        else:
            form.flag.errors += [f'Invalid flag for service {service}']
        
            
    return render_template('submit.html', form=form)

    
####### ONLY FOR THE CHECKER. DO NOT TOUCH THE FOLLOWING ROUTE IF YOU LIKE SLA ###
@app.route('/new_tick', methods=['GET', 'PUT'])
def new_tick():

    # create the challenge
    if request.method == 'GET':
        session['nonce'] = secrets.token_urlsafe(16)
        return jsonify({'nonce': session['nonce']})

    raw_data = request.get_data().decode()
    try:
        data = jwt.decode(raw_data, app.config['CHECKER_PUBLICK_KEY'], algorithms=['ES256'])
        assert data['nonce'] == session['nonce']
    except (jwt.InvalidSignatureError, AssertionError):
        return jsonify({'result': 'denied'})

    # takes the last submitted tick
    flagstore = int(data['flagstore'])
    last_tick = Tick.query.get(g.tick)
    
    # check if the last tick has the flag for the correct flagstore
    flag = last_tick.flagstore_1 if flagstore == 1 else last_tick.flagstore_2
    
    # if there is one create another tick
    if flag:
        last_tick = Tick()

    # update the flagstore
    if flagstore == 1:
        last_tick.flagstore_1 = data['flag']
    else:
        last_tick.flagstore_2 = data['flag']

    db.session.add(last_tick)
    db.session.commit()

    # change the tick -12 to not running
    if g.tick > 12:
        old_tick = Tick.query.get(last_tick.id - 12)
        old_tick.running = False
        db.session.add(old_tick)
        db.session.commit()
    #if g.tick > 10:
    #    tokens = Service.query.filter(Service.tick == g.tick - 10).all()
    #    for token in tokens:
    #        db.session.delete(token)
    #    db.session.commit()

    # TODO change tick -5 to not running
    return jsonify({'result': 'ok'})
        
@app.route('/get_seeds', methods=['GET', 'POST'])
def get_seeds():
    
    if request.method == 'GET':
        session['nonce'] = secrets.token_urlsafe(16)
        return jsonify({'nonce': session['nonce']})

    raw_data = request.get_data().decode()
    try:
        data = jwt.decode(raw_data, app.config['CHECKER_PUBLICK_KEY'], algorithms=['ES256'])
        assert data['nonce'] == session['nonce']
    except (jwt.InvalidSignatureError, AssertionError):
        return jsonify({'result': 'denied'})
    

    service = Service.query.get(data['token'])
    if not service:
        return jsonify({'result': 'error: Token not found'})
    seeds = service.seeds
    data = {}
    data['result'] = 'ok'
    data['seeds'] = [x.seed for x in seeds]
    return jsonify(data)

def install_db():
    print('Initializing db')
    
    with app.app_context():
        db.create_all()
        try:
            db.session.commit()
        except Exception as e:
            print('Problem creating the db. ' + e.msg)
            return
        test_tick = Tick('test_flag_1', 'test_flag_2')
        #test_tick.id = 1
        nop_team = Team('Nop_Team', secrets.token_hex(4))
        db.session.add(test_tick)
        db.session.add(nop_team)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            pass

    print('Database initialized successfully') 

if __name__ == '__main__':

    if 'install' in sys.argv:
        install_db()
    else:
        app.run(debug=True)