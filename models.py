from cerise import db
from flask_login import UserMixin
from flask_wtf import Form
from wtforms import StringField, PasswordField, validators, FieldList, 
from wtforms import Form as wtf.Form

class Step(db.EmbeddedDocument):
    action = db.StringField(max_length=255)
    workdir = db.StringField(max_length=255)

class Project(db.EmbeddedDocument):
    name = db.StringField(max_length=255)
    gitrepo = db.URLField(max_length=255)
    steps = db.ListField(db.EmbeddedDocumentField(Step), max_length=25)

class User(db.Document, UserMixin):
    username = db.StringField(max_length=25)
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    port_offset = db.IntField()
    active = db.BooleanField(default=True)
    projects = db.ListField(db.EmbeddedDocumentField(Project), max_length=25)

class LoginForm(Form):
    username = StringField('username', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])

class RegisterForm(Form):
    username = StringField('username', [
        validators.Length(min=4, max=25, message='length must be > 6 and < 25')
    ])
    email = StringField('email', [
        validators.Length(min=4, max=50, message='length must be > 4 and < 50'),
        validators.Email(message='must be valid email address')])
    password = PasswordField('password', [
        validators.Length(min=6, max=25, message='length must be > 6 and < 25'), 
        validators.EqualTo('confirm', message='passwords must match')])
    confirm = PasswordField('retype password')

class StepForm(wtf.Form):
    step = StringField('build step', [
        validators.Length(max=255, message='length must be shorter than 255 characters')
    ])
    workdir = StringField('workdir', [
        validators.Length(max=255, message='length must be shorter than 255 characters')
    ])

class ProjectForm(Form):
    name = StringField('project name', [
        validators.Length(max=255, message='length must be shorter than 255 characters')])
    gitrepo = StringField('git repo', [
        validators.Length(max=255, message='length must be shorter than 255 characters')])
    steps = FieldList(FormField(StepForm), min_entries=1, max_entries=25)