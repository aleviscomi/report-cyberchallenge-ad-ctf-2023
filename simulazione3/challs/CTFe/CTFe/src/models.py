
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Team(db.Model):
    __tablename__ = 'team'

    team_name = db.Column(db.String(18), primary_key=True)
    password_hash = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer(), nullable=False)

    @property
    def password(self):
        raise AttributeError('Maybe you want the hash..')

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def verify_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    def __init__(self, username, password):
        self.team_name = username
        self.password = password
        self.points = 0
        super().__init__()

class Tick(db.Model):
    __tablename__ = 'tick'
    
    id = db.Column(db.Integer, primary_key=True)
    running = db.Column(db.Boolean, nullable=False)
    flagstore_1 = db.Column('flagstore_1', db.String(32), nullable=True) 
    flagstore_2 = db.Column('flagstore_2', db.String(32), nullable=True)
    attack_tokens = db.relationship("Service")
    
    def __init__(self, flag1=None, flag2=None) -> None:
        self.flagstore_1 = flag1
        self.flagstore_2 = flag2
        self.running = True
        

class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.String(33), primary_key=True)
    flag = db.Column(db.String(37), nullable=False)
    service = db.Column(db.Integer, nullable=False)
    tick = db.Column(db.Integer, db.ForeignKey('tick.id'))
    seeds = db.relationship("ServiceSeeds", cascade="all, delete", order_by=lambda: ServiceSeeds.id) 
    
    def __init__(self, token, flag, service):
        self.id = token
        self.flag = flag
        self.service = service

class ServiceSeeds(db.Model):
    __tablename__ = 'eightbitroulette_seeds'

    id = db.Column(db.Integer(), primary_key=True)
    token = db.Column(db.String(33), db.ForeignKey('service.id'))
    seed = db.Column(db.Integer(), nullable=True)