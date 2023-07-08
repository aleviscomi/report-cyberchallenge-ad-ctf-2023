import sys
import os
from flask import Flask,g,session
from api import api
from interface import ui
from flask_bootstrap import Bootstrap
from models import db, User


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')
DBHOST = os.environ.get('DBHOST', '')
DBUSER = os.environ.get('DBUSER', 'root')
DBPASS = os.environ.get('DBPASS', '')
DBSCHEMA = os.environ.get('DBSCHEMA', '')
app.config['WTF_CSRF_ENABLED'] = False

DB_URI = f'mysql+pymysql://{DBUSER}:{DBPASS}@{DBHOST}/{DBSCHEMA}'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = '/srv/uploads/'
app.config['MAX_CONTENT_PATH'] = 400

@app.before_request
def check_user():
    g.logged = False
    if 'user_id' not in session:
        return

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user:
        g.user = user
        g.logged = True
    else:
        del session['user_id']

app.register_blueprint(ui)
app.register_blueprint(api)
db.init_app(app)
Bootstrap(app)

if __name__ == '__main__':
    if 'install' in sys.argv:
        from models import *
        with app.app_context() as ctx:
            db.create_all()
            db.session.commit()
        quit()
    app.run(port=5000, debug=True, host='0.0.0.0')