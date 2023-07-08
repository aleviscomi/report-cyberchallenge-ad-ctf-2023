import os
import glob
from flask import Blueprint, request, current_app, abort, g
from flask.json import jsonify
from utils import  auth, project_exists
from models import *

api = Blueprint('api', __name__)


@api.route('/api/search/<uid>/', methods=['POST'])
@auth
@project_exists
def search_project(uid):
    if g.user not in g.project.users:
        abort(401)
    if not request.is_json:
        return jsonify({'result': 'error: Request is not a valid json. Did you forget to set the content/type?'})
    
    data = request.json

    try:
        file_search = data['search']
    except:
        return jsonify({'result': 'error: search attribute not found'})
    path = current_app.config['UPLOAD_FOLDER'] + '/' + uid
   
    if not os.path.isdir(path): # no files in this project
        return jsonify({'result': 'ok', 'files': []}) 

    files = glob.glob(path + '/' + file_search + '*')
    files = [os.path.basename(x) for x in files]
    return jsonify({'result': 'ok', 'files': files})


