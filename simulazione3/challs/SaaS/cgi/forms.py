from flask_wtf import FlaskForm
from wtforms.fields.simple import PasswordField, SubmitField, TextField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import DataRequired, Length
from models import *


class LoginForm(FlaskForm):
    username = TextField('Username', validators=[
        DataRequired('Username required!'),
        Length(min=10, max=18, message="Username must be between 10 and 18 Characters")])
    password = PasswordField('Password', validators=[
        DataRequired('Password required!')
    ])
    submit = SubmitField('Login')

    def validate(self):
        valid = super().validate()
        
        # do the login
        username = self.username.data
        password = self.password.data

        user = User.query.filter(User.username == username).first()
        if not user or not user.verify_password(password):
            self.username.errors += ['Wrong Credentials']
            valid = False
        
        return valid


class RegisterForm(FlaskForm):
    username = TextField('Username', validators=[
        DataRequired('Username required!'),
        Length(min=10,max=18, message="Username length must be between 10 and 18 Characters")
        ])
    password = PasswordField('Password', validators=[
        DataRequired('Password required!'),
        Length(min=10, message="Password must be of at least 10 characters")
    ])
    submit = SubmitField('Register')

    def validate(self):
        valid = super().validate()
        
        username = self.username.data

        user = User.query.filter(User.username == username).first()
        if user:
            self.username.errors += ['Username already used']
            valid = False
        
        return valid


class NewProjectForm(FlaskForm):
    name = TextField('Project name', validators=[
        DataRequired('Project name required!'),
        Length(min=6, max=20, message="The name length must be between 6 and 20 Characters")
    ])
    submit = SubmitField('Create !')

    def validate(self):
        valid = super().validate()
        
        name = self.name.data

        p = Project.query.filter(Project.name == name).first()
        if p:
            self.name.errors += ['Project name already used']
            valid = False
        
        return valid
    
class UploadForm(FlaskForm):
    file = FileField("Binary", validators=[FileRequired()])
    submit = SubmitField("upload")