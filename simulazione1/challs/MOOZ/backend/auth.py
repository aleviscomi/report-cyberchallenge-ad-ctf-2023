from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, validators
from sqlalchemy.exc import IntegrityError
import bcrypt, random

from backend import db
from .application import avatar_list

bp = Blueprint('auth', __name__, url_prefix='/auth')
login_manager = LoginManager()


@login_manager.unauthorized_handler
def unauth_handler():
    return jsonify({"status":"fail","message":"please login"}), 401


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    key = db.Column(db.BigInteger, unique=False, nullable=False)
    avatar = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return '<User {}, {}>'.format(self.id, self.email)

    def get_id(self):
        return self.email

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(email=user_id).first()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        form = request.json
        user = User(username = form['username'], 
                    email = form['email'], 
                    password = bcrypt.hashpw(form['password'].encode(), bcrypt.gensalt()),
                    key = random.getrandbits(56),
                    avatar = random.choice(avatar_list()))
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"status":"ok","message":"Register successful, please login"})

        except IntegrityError as e:
            db.session.rollback()
            return jsonify({"status":"fail","message":'Register failed {}'.format(e)})
    return jsonify({"status":"fail", "message":"please register"})

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        form = request.json
        user = User.query.filter_by(email=form['email']).first()
        if user is not None and bcrypt.checkpw(form['password'].encode(), user.password):
            login_user(user)
            user_arr = {"email":user.email, "username":user.username , "id":user.id, "avatar":user.avatar, "key":str(user.key)}
            return jsonify({"status":"ok","message":"Login successful","user":user_arr})
        else:
            return jsonify({"status":"fail","message":'Wrong username or pasword!'})
    return jsonify({"status":"fail","message":"please login"})

@bp.route("/check_login")
@login_required
def check_login():
    user_arr = {"email":current_user.email, "username":current_user.username , "id":current_user.id, "avatar":current_user.avatar, "key":str(current_user.key)}
    return jsonify({"status":"ok","message":"Login successful","user":user_arr})


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"status":"ok","message":"Logout successful"})

@bp.route("/users")
@login_required
def users_list():
    users = User.query.all()
    users_arr = [{"email":el.email, "username":el.username ,"id":el.id, "avatar":el.avatar} for el in users ]
    return jsonify({"status":"ok","users":users_arr})

@bp.route("/users/<int:userid>", methods=('GET','POST'))
@login_required
def user_info_changeavatar(userid):
    if userid != current_user.id: 
        return jsonify({"status":"fail","message":"cannot get other users info"}),403
    user = User.query.filter_by(id=userid).first()
    # user_arr = (user.email, user.username ,user.id, user.avatar, user.key)
    user_arr = {"email":user.email, "username":user.username , "id":user.id, "avatar":user.avatar, "key":str(user.key)}
    if request.method == 'POST':
        try:
            form = request.json
            avatar = form['avatar']
            user.avatar = avatar
            db.session.commit()
        except:
            return jsonify({"status":"fail","message":"cannot edit avatar"}),500
    return jsonify({"status":"ok","user":user_arr})