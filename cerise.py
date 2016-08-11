from flask import Flask, request, render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_mongoengine import MongoEngine
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
import os, boto3, subprocess, requests
from configparser import ConfigParser
from urllib.parse import urlparse

app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')
db = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)
ec2 = boto3.resource('ec2')

def create_master(user):
    directory = "/build/" + user.username
    os.mkdir(directory)
    c = ConfigParser()
    c.read('./conf/default.conf')
    c.set('main', 'user', user.username)
    with open('/build/' + user.username + '.conf') as f:
        c.write(f)
    subprocess.call(['ln', '-s', './conf/caiman.cfg', 'directory' + '/master.cfg'])
    subprocess.call(['buildbot', 'create-master'], cwd=directory)
    subprocess.Popen(['buildbot', 'start'], cwd=directory)

@login_manager.user_loader
def load_user(id):
    user = User.objects.get(username=id)
    if not user:
        return None
    return user

@app.route('/')
def index():
    if current_user.is_authenticated:
	    return render_template('index.html', user=current_user)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST' and form():
        user = User.objects.get(username=form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', title='login', form=form)

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate():
        user = User(username=form.username.data, email=form.email.data)
        user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
        user.port_offset = randint(1, 2000)
        user.save()
        login_user(user)
        create_master(user)
        return redirect(url_for('index'))
    return render_template('/register', form=form)


@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/update', methods=['GET'])
@login_required
def update():
    port = sum([curent_user.port_offset, 20000])
    r = requests.get('localhost:' + port + "/builds")
    return(r.json())

if __name__ == "__main__":
    for user in User.objects:
        directory = "/build/" + user.username
        subprocess.Popen(['buildbot', 'start'], cwd=directory)
    app.run(host='0.0.0.0')
