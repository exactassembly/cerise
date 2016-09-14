from .cerise import db
from flask_login import UserMixin
from flask_wtf import Form
from wtforms import StringField, PasswordField, validators, FieldList, FormField
from wtforms import Form as wtForm

class Step(db.EmbeddedDocument):
    action = db.StringField(max_length=255)
    workdir = db.StringField(max_length=255)

class SubProject(db.EmbeddedDocument):
    id = db.ObjectIdField(required=True, default=lambda: ObjectId())
    name = db.StringField(max_length=255)
    url = db.StringField(max_length=255)
    steps = db.EmbeddedDocumentListField(Step, max_length=25)

class Project(db.EmbeddedDocument):
    name = db.StringField(max_length=255)
    url = db.StringField(max_length=255)
    subs = db.EmbeddedDocumentListField(SubProject, max_length=25)
    steps = db.EmbeddedDocumentListField(Step, max_length=25)

class AWS(db.EmbeddedDocument):
    keyID = db.StringField(max_length=255)
    accessKey = db.StringField(max_length=255)

class Group(db.Document):
    name = db.StringField(max_length=50)
    port_offset = db.IntField()
    aws = db.EmbeddedDocumentField(AWS)
    pid = db.IntField()
    projects = db.EmbeddedDocumentListField(Project, max_length=50)
    users = db.ListField(db.ReferenceField('User'), max_length=100)

class User(db.Document, UserMixin):
    username = db.StringField(max_length=25)
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    groups = db.ListField(db.ReferenceField(Group), max_length=25)

class LoginForm(Form):
    username = StringField('username', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])

class RegisterForm(Form):
    username = StringField('username', [
        validators.Length(min=4, max=25, message='length must be > 6 and < 25'),
        validators.Regexp('^\w+$', message='letters, numbers, and underscores only')
    ])
    email = StringField('email', [
        validators.Length(min=4, max=50, message='length must be > 4 and < 50'),
        validators.Email(message='must be valid email address')
    ])
    password = PasswordField('password', [
        validators.Length(min=6, max=25, message='length must be > 6 and < 25'), 
        validators.EqualTo('confirm', message='passwords must match'),
    ])
    confirm = PasswordField('retype password')

class StepForm(wtForm):
    step = StringField('build step', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])
    workdir = StringField('workdir', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])   

class ProjectForm(Form):
    id = StringField('project id', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])
    sub = StringField('sub-project', [
        validators.Length(max=255, message='length must be shorter than 255 characters')
    ])
    name = StringField('project name', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])
    url = StringField('git repo', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])
    steps = FieldList(FormField(StepForm), min_entries=1, max_entries=25)

class AWSForm(Form):
    keyID = StringField('project name', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])
    accessKey = StringField('access key', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])