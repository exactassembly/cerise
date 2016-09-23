from flask_wtf import Form
from wtforms import StringField, PasswordField, validators, FieldList, FormField
from wtforms import Form as wtForm

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
    group = StringField('group')
    ref = StringField('ref')
    confirm = PasswordField('retype password')
