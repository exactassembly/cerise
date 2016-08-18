from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_mongoengine import MongoEngine
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
import os, boto3, subprocess, requests, pickle
from configparser import ConfigParser
from urllib.parse import urlparse
from random import randint


app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')
db = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)
ec2 = boto3.resource('ec2')

def create_master(user):
    directory = "/build/" + user.username
    if not os.path.exists(directory):
        os.mkdir(directory)
    c = ConfigParser()
    c.read('./conf/default.conf')
    c.set('main', 'user', user.username)
    with open(directory + '/user.conf', 'w') as f:
        c.write(f)
    subprocess.call(['ln', '-s', os.getcwd() + '/conf/caiman.cfg', directory + '/master.cfg'])
    subprocess.call(['buildbot', 'create-master'], cwd=directory)
    subprocess.Popen(['buildbot', 'start'], cwd=directory)

@login_manager.user_loader
def load_user(id):
    try:
        user = User.objects.get(id=id)
        return user
    except:
        return None

@app.route('/')
def index():
    if current_user.is_authenticated:
	    return render_template('index.html', user=current_user['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    rForm = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST' and form.validate_on_submit():
        user = User.objects.get(username=form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', title='login', form=form, rForm=rForm)

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if not User.objects.filter(username=form.username.data):
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
            user.port_offset = randint(1, 2000)
            user.save()
            login_user(user)
            create_master(user)
            return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = ProjectForm()
    projects = current_user['projects']
    if request.method == 'POST':
        if form.validate_on_submit():
            if not current_user.projects.filter(name=form.name.data):
                newProject = Project(name=form.name.data)
                newProject.gitrepo = form.gitrepo.data
                newProject.steps = []
                for step in form.steps.data:
                    newProject['steps'].append(Step(action=step['step'], workdir=step['workdir']))
                current_user.projects.append(newProject)
                current_user.save()
                subprocess.Popen(['buildbot', 'reconfig'], cwd="/build/" + current_user.username)            
            else:
                flash("Project name already exists.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(u"Error in the %s field - %s" % (
                        getattr(form, field).label.text,
                        error
                    ))
    return render_template('account.html', form=form, projects=projects)

@app.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    form = ProjectForm()
    if request.method == 'GET':
        currentProject = request.args.get('name')
        project = current_user.projects.get(name=currentProject)
        return render_template('project.html', project=project, form=form)
    if request.method == 'POST':
        if form.validate_on_submit():
            project = current_user.projects.get(name=request.form.get('name'))
            project.gitrepo = form.gitrepo.data
            project.steps = []
            for step in form.steps.data:
                project['steps'].append(Step(action=step['step'], workdir=step['workdir']))
            current_user.save()
            subprocess.Popen(['buildbot', 'reconfig'], cwd="/build/" + current_user.username)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(u"Error in the %s field - %s" % (
                        getattr(form, field).label.text,
                        error
                    ))
        return redirect('/project?name=' + request.form.get('name'))

@app.route('/api/<path:path>', methods=['GET'])
@login_required
def builders(path):
    port = sum([current_user.port_offset, 20000])
    r = requests.get("localhost:" + str(port) + "/json/" + path)
    return(r.json())

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    for user in User.objects:
        directory = "/build/" + user.username
        subprocess.Popen(['buildbot', 'start'], cwd=directory)
    app.run(host='0.0.0.0')
