from re import RegexFlag
from secrets import choice
from flask_wtf import FlaskForm
from wtforms.fields.core import SelectField
from wtforms.fields.simple import PasswordField, SubmitField, TextField
from wtforms.validators import DataRequired, Length, Regexp
from models import Team, Tick
from flask import g

class LoginForm(FlaskForm):
    team_name = TextField('Team Name', validators=[
        DataRequired('Username required!'),
        Length(min=10, max=18, message="Team Name length must be between 10 and 18 Characters")])
    password = PasswordField('Password', validators=[
        DataRequired('Password required!')
    ])
    submit = SubmitField('Login')

    def validate(self):
        initial = super().validate()
        if not initial:
            return False
        
        # do the login
        team_name = self.team_name.data
        password = self.password.data

        team = Team.query.get(team_name)
        if not team or not team.verify_password(password):
            self.team_name.errors += ['Wrong Credentials']
            return False
        
        return True


class RegisterForm(FlaskForm):
    team_name = TextField('Team Name', validators=[
        DataRequired('Username required!'),
        Length(min=10, max=18, message="Team Name length must be between 10 and 18 Characters")
        ])
    password = PasswordField('Password', validators=[
        DataRequired('Password required!'),
        Length(min=10, message="Password must be of at least 10 characters")
    ])
    submit = SubmitField('Register')

    def validate(self):
        initial = super().validate()
        if not initial:
            return False
        
        team_name = self.team_name.data

        team = Team.query.get(team_name)
        if team:
            self.team_name.errors += ['Team name already registerd']
            return False
        
        return True

class FlagForm(FlaskForm):
    flag = TextField('Flag', validators=[
        DataRequired('The flag is required'),
        Regexp(r'FKE\{[0-9a-f]{32}\}', message='Invalid Flag Format')
    ])
    team = TextField('Team', validators=[
        DataRequired('The flag is required'),
    ])
    service = SelectField('Service', choices=[(1, 'Cat roulette'), (2, 'NotEBook')], validators=[DataRequired('The tick is required')])       
    submit = SubmitField('Send')

    def validate(self):
        initial = super().validate()

        team = Team.query.get(self.team.data)
        if not team:
            self.team.errors += ['This team does not exist']
            initial = False
        
        try:
            assert int(self.service.data) in (1,2)
        except:
            self.service.errors += ['Invalid Service']
            initial = False
        return initial

class ServiceForm(FlaskForm):
    team = TextField('Who are you going to attack?', validators=[
        DataRequired('The team name is required'),
    ])
    tick = TextField('Tick', validators=[
        DataRequired('The tick is required'),
    ])
    service = SelectField('Service', choices=[(1, 'Cat roulette'), (2, 'NotEBook')], validators=[DataRequired('The tick is required')])       
    submit = SubmitField('Attack!')

    def __init__(self):
        
        
        super().__init__(tick=g.tick)
        

    def validate(self):
        valid = super().validate()

        team = Team.query.get(self.team.data)
        if not team:
            self.team.errors += ['This team does not exist']
            return False

        if team == g.user:
            self.team.errors += ['You cannot attack yourself!']
            valid = False
        try:
            assert int(self.service.data) in (1,2)
        except:
            self.service.errors += ['Invalid Service']
            valid = False
        tick = Tick.query.get(self.tick.data)
        if not tick:
            self.tick.errors += ['Tick invalid']
            valid = False

        return valid