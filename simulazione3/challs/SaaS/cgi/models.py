from enum import unique
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import uuid


db = SQLAlchemy()


project_users = db.Table('project_users',
    db.Column('user', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('project', db.String(36), db.ForeignKey('project.project_id'), primary_key=True),
)


class Project(db.Model):
    project_id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(20), nullable=False)
    users = db.relationship('User', secondary=project_users,
        back_populates='projects')
    files = db.relationship("PFiles")
    
    def __init__(self, name, owner):
        self.name = name
        self.users = [owner]

class PFiles(db.Model):
    uid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    filename = db.Column(db.String(36), unique=True)
    project_id = db.Column(db.String(36), db.ForeignKey('project.project_id'))
    comment = db.Column(db.Text, nullable=True)
    disass = db.Column(db.Text)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(18))
    password_hash = db.Column(db.String(120))
    
    projects = db.relationship('Project', secondary=project_users,
        back_populates='users')

    @property
    def password(self):
        raise AttributeError('Maybe you want the hash..')

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def verify_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        super().__init__()

