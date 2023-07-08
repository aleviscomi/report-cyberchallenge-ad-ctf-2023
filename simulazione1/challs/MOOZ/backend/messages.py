import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort, jsonify
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, validators
from sqlalchemy import or_, and_

from backend import db
from . import auth
import json
from . import crypto_func


bp = Blueprint('messages', __name__)

class Message(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    tstamp = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    user_from_id = db.Column(db.Integer, db.ForeignKey(auth.User.id), nullable=False)
    user_to_id = db.Column(db.Integer, db.ForeignKey(auth.User.id), nullable=False)

    user_to = db.relationship('User', backref=db.backref('messages', lazy=True), foreign_keys='Message.user_to_id')
    user_from = db.relationship('User', backref=db.backref('sent', lazy=True), foreign_keys='Message.user_from_id')

    def __repr__(self):
        return '<Message {}, {}, {}>'.format(self.user_from, self.user_to, self.title)

def formatdate(datetimeobj):
    return datetime.datetime.strftime(datetimeobj,"%d/%m/%Y %H:%M:%S")

@bp.route('/send', methods=('GET', 'POST'))
@login_required
def send():
    if request.method == 'POST':
        try:
            form = request.json
            user_to = auth.User.query.get_or_404(int(form['receiver']))
            msg = Message(body=form['body'],
                          user_from=current_user, user_to=user_to)
            db.session.add(msg)
            db.session.commit()
            return jsonify({"status":"ok","message":"Message Sent"})
        except Exception as e:
            return jsonify({"status":"fail","message":"Cannot Send Message {}".format(e)})
    return jsonify({"status":"ok","message":"Send Messages"})

@bp.route('/messages/<int:sender>/<int:receiver>')
@login_required
def messages(sender,receiver): # no need to access control because of strong crypto
    if sender != receiver:
        messages = Message.query.filter(
            and_(
            and_(or_(Message.user_from_id==sender, Message.user_from_id==receiver), 
            or_(Message.user_to_id==receiver, Message.user_to_id==sender)),
            Message.user_to_id!= Message.user_from_id)
            )
    else:
        messages = Message.query.filter(or_(Message.user_from_id==sender, Message.user_from_id==receiver), or_(Message.user_to_id==receiver, Message.user_to_id==sender))
    messages = [{"id":mes.id, "userid":mes.user_from_id, "body":mes.body, "tstamp": formatdate(mes.tstamp)} for mes in messages]
    messages_string = json.dumps(messages)
    # encrypt message json string
    # perform dh to get symmetric then encrypt
    public_receiver = crypto_func.get_public(auth.User.query.get_or_404(int(receiver)).key)
    symmetric = crypto_func.get_symmetric(public_receiver,auth.User.query.get_or_404(int(sender)).key)
    messages_string_enc = crypto_func.encrypt(messages_string,symmetric)
    return jsonify({"status":"ok","message":"Retrieved Messages","data":messages_string_enc})