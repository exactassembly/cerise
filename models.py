from cerise import db
from flask_login import UserMixin
from wtforms import Form, StringField, PasswordField, validators, FieldList

class Project(db.EmbeddedDocument):
    name = db.StringField(max_length=255)
    gitrepo = db.URLField(max_length=255)
    steps = db.ListField(db.StringField(max_length=255))

class User(db.Document, UserMixin):
    username = db.StringField(max_length=25)
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    port_offset = db.IntField()
    active = db.BooleanField(default=True)
    projects = db.ListField(db.EmbeddedDocumentField(Project))

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

class ProjectForm(Form):
    gitrepo = StringField('git repo', [
        validators.Length(max=255, message='length must be shorter than 255 characters')])
    steps = FieldList(StringField('build step', [
        validators.Length(max=255, message='length must be shorter than 255 characters')
    ]), min_entries=1, max_entries=5)
