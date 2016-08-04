from flask import Flask, render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.wtf import 
from flask.ext.mongoengine import MongoEngine
from werkzeug.security import check_password_hash
from urllib.parse import urlparse
import boto3
app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')

db = MongoEngine(app)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)

@login_manager.user_loader
def load_user(user_id):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        return None
    return User(user["user_id"])

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
        user = User.objects.get(user_id=form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            login_user(user_obj)
            return redirect(url_for('/'))
            

    return render_template('login.html', title='login', form=form)
            

@app.route('/spinup', methods=['POST'])
@login_required
def spinup():
    parse = urlparse(request.form['repo'])
    if parse['scheme'] and parse.['netloc']:
        GIT_REPO = request.form['repo']
    if len(request.form['token'].split()) == 1 and request.form['token'].isalnum():
        GIT_TOKEN = request.form['token']
    if 

@app.route('/buildlight')
@login_required
def buildlight():

