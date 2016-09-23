from flask_wtf import Form
from wtforms import StringField, PasswordField, validators, FieldList, FormField
from wtforms import Form as wtForm

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
    accessKey = PasswordField('access key', [
        validators.Length(max=255, message='length must be shorter than 255 characters'),
        validators.DataRequired()
    ])