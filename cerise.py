from flask import Flask, render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.wtf import 
from flask.ext.mongoengine import MongoEngine
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
import boto3
app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')

db = MongoEngine(app)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)

class Project(db.Document):
    gitrepo = db.URLField(max_length=255)
    steps = db.ListField(db.StringField(max_length=255))

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
    if request.method == 'POST' and form.validate_on_submit():
        user = User.objects.get(user_id=form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            login_user(user)
            return redirect(url_for('/'))
    return render_template('login.html', title='login', form=form)

@app.route('/register', methods=['POST'])
def register():
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
        user.save()
        login_user(user)

@app.route('/spinup', methods=['POST'])
@login_required
def spinup():
    

@app.route('/account')
@login_required
def account():
    return render_template('account.html')
