from flask import Flask, render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.mongoengine import MongoEngine
from wtforms import Form, StringField, PasswordField, validators, FieldList
from werkzeug.security import generate_password_hash, check_password_hash
import urlparse
import boto3
app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')

db = MongoEngine(app)
ec2 = boto3.resource('ec2')

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    projects = ListField(EmbeddedDocumentField(Project))

class Project(db.EmbeddedDocument):
    name = db.StringField(max_length=255)
    gitrepo = db.URLField(max_length=255)
    steps = db.ListField(db.StringField(max_length=255))

class LoginForm(Form):
    email = StringField('email', [validators.DataRequired()])
    password = PasswordField('password', [validators.DataRequired()])

class RegisterForm(Form):
    email = StringField('email', [
        validators.Length(min=4, max=25, message='length must be > 4 and < 25')])
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

@login_manager.user_loader
def load_user(user_id):
    user = User.objects.get(user_id)
    if not user:
        return None
    return user

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST' and form.validate_on_submit():
        user = User.objects.get(user_id=form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            login_user(user)
            return redirect(url_for('/'))
    return render_template('login.html', title='login', form=form)

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
        user.save()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('/register', form=form)

#@app.route('/build', methods=['POST'])
#@login_required
#def build():
    

@app.route('/account')
@login_required
def account():
    return render_template('account.html')
