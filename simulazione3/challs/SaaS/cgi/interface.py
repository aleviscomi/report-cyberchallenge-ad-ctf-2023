import os
from flask import Blueprint, render_template, session
from flask import redirect, url_for, flash, abort, g, current_app, send_file
from forms import LoginForm, RegisterForm, NewProjectForm, UploadForm
from werkzeug.utils import secure_filename
from utils import  auth, disasm, not_auth, project_exists
from models import *
import sys

ui = Blueprint('interface', __name__)


@ui.get('/')
def index():
    return render_template('index.html')
        
@ui.route('/register', methods=['GET', 'POST'])
@not_auth
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        flash('The registration was successful! Happy reversing')
        return redirect(url_for('interface.index'))


    return render_template('register.html', form=form)


@ui.route('/login', methods=['GET', 'POST'])
@not_auth
def login():

    form = LoginForm()
    if form.validate_on_submit():
        session['user_id'] = User.query.filter(User.username == form.username.data).first().id
        flash('The login was successful! Happy reversing', category='success')
        return redirect(url_for('interface.index'))

    return render_template('login.html', form=form)

@ui.route('/logout', methods=['GET'])
@auth
def logout():
    del session['user_id']
    flash('Signed out', category='success')
    return redirect(url_for('interface.index'))


@ui.route('/projects', methods=['GET', 'POST'])
@auth
def projects():
    projects = g.user.projects
    
    form = NewProjectForm()
    if form.validate_on_submit():
        name = form.name.data
        new_project = Project(name, g.user)
    
        db.session.add(new_project)
        db.session.commit()

    return render_template('projects.html', projects=projects, form=form)


@ui.route('/project/<uid>', methods=['GET', 'POST'])
@auth
@project_exists
def project(uid):
    # check if the user has access to the project
    if g.user not in g.project.users:
        abort(401)
    
    form = UploadForm()

    if form.validate_on_submit():
        directory = current_app.config['UPLOAD_FOLDER'] + uid
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass
        filename = secure_filename(form.file.data.filename)
        pfile = PFiles.query.filter((PFiles.filename == filename) & (PFiles.project_id == uid)).first()
        if not pfile:
            pfile = PFiles()
        
        full_path = directory + '/' + filename
        form.file.data.save(full_path)
 
        #pfile = PFiles()
        pfile.filename = filename
        with open(full_path, 'rb') as f:
            raw = f.read()
        

        pfile.disass = disasm(raw)
        
        g.project.files.append(pfile)

        db.session.add(g.project)
        db.session.commit()

    return render_template('project.html', form=form)

@ui.route('/project/<uid>/file/<file_uid>', methods=['GET', 'POST'])
@auth
@project_exists
def file(uid, file_uid):
    # check if the user has access to the project
    if g.user not in g.project.users:
        abort(401)
    
    file = PFiles.query.filter(PFiles.uid == file_uid).first()

    if not file:
        abort(404)
    

    return render_template('file.html', file=file)

@ui.route('/project/<uid>/file/<file_uid>/download', methods=['GET', 'POST'])
@auth
@project_exists
def download(uid, file_uid):
    # check if the user has access to the project
    if g.user not in g.project.users:
        abort(401)
    
    file = PFiles.query.filter(PFiles.uid == file_uid).first()

    if not file:
        abort(404)
    

    return send_file(current_app.config['UPLOAD_FOLDER'] + uid + '/' + file.filename)


