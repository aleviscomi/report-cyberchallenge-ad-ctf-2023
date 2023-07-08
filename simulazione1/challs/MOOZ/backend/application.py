from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, current_app, Response
)
from flask_login import login_required, current_user

from backend import db
import os

bp = Blueprint('application', __name__)

@bp.route('/')
def index():
    return jsonify({"status":"ok", "message":"it works ;)"})

def avatar_list():
    avatars_path = os.path.join(current_app.instance_path,'..','avatars')
    return [f for f in os.listdir(avatars_path) if os.path.isfile(os.path.join(avatars_path, f))]

@bp.route('/utils/avatar_list')
def get_avatar_list():
    avatar_list_var = avatar_list()
    return jsonify({"status":"ok","avatars":avatar_list_var})

@bp.route('/utils/avatar')
def get_avatar():
    try:
        filename = request.args.get('filename')
        avatars_path = os.path.join(current_app.instance_path,'..','avatars')
        if os.path.isfile(os.path.join(avatars_path, filename)):
            f = open(os.path.join(avatars_path, filename),'rb')
            cont=f.read()
            resp = Response(cont, mimetype='image/png')
            return resp
    except Exception as e:
        print(e)

    return jsonify({"status":"fail","message":"avatar doesn't exists"}), 404