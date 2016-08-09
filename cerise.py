from flask import Flask, render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.mongoengine import MongoEngine
from wtforms import Form, StringField, PasswordField, validators, FieldList
from werkzeug.security import generate_password_hash, check_password_hash
import os, boto3, urlparse, subprocess
from ConfigParser import SafeConfigParser

app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')

db = MongoEngine(app)
ec2 = boto3.resource('ec2')

class User(db.Document, UserMixin):
    username = db.StringField(max_length=25)
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    port_offset = db.IntField()
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

def create_master(user):
    directory = "/build/" + user.username
    os.mkdir(directory)
    c = SafeConfigParser()
    c.read('./conf/default.conf')
    c.set('main', 'user', user.username)
    with open('/build/' + user.username + '.conf') as f:
        c.write(f)
    subprocess.call(['ln', '-s', './conf/caiman.cfg', 'directory' + '/master.cfg'])
    subprocess.call(['buildbot', 'create-master'], cwd=directory)
    subprocess.Popen(['buildbot', 'start'], cwd=directory))

@login_manager.user_loader
def load_user(user_id):
    user = User.objects.get(username=user_id)
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
        user = User.objects.get(username=form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', title='login', form=form)

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
        user.port_offset = randint(1, 2000)
        user.save()
        login_user(user)
        create_master(user)
        return redirect(url_for('index'))
    return render_template('/register', form=form)

#@app.route('/build', methods=['POST'])
#@login_required
#def build():
    

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

if __name__ == "__main__":
    for user in User.objects:
        directory = "/build/" + user.username
        subprocess.Popen(['buildbot', 'start'], cwd=directory)
    app.run()