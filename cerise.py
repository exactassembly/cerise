from flask import Flask, request, render_template, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_mongoengine import MongoEngine

from werkzeug.security import generate_password_hash, check_password_hash
from configparser import ConfigParser
from urllib.parse import urlparse
from random import randint
from time import sleep
import os, boto3, subprocess, requests

from .models import *
from .helpers import *

app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')
db = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)
ec2 = boto3.resource('ec2')

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
        user = User.objects.get(username__iexact=form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', title='login', form=form, rForm=rForm)

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if not User.objects(username=form.username.data):
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
            user.port_offset = randint(1, 2000)
            user.save()
            login_user(user)
            create_master(user)
            return redirect(url_for('aws'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    projects = current_user.projects
    groupProjects = current_user.group.projects
    processLive = False
    if not current_user.aws:
        return redirect(url_for(aws)) # require user to offer AWS information before accessing main UI
    if current_user.pid:
        try:
            os.kill(current_user.pid, 0)
            processLive = True
        except OSError:
            processLive = False
    return render_template('account.html', form=form, projects=projects, groupProjects=groupProjects, processLive=processLive)

@app.route('/account/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = (current_user['username'], current_user['email'])
    if request.method == 'POST':
        if request.form.get('username'):
            current_user['username'] = request.form.get('username')
        if request.form.get('email'):
            current_user['email'] = request.form.get('email')
        if request.form.get('password'):
            current_user['password'] = request.form.get('password')            
    return render_template('profile.html', user=user)

@app.route('/account/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        if request.form.get('parent'):
            form = SubForm()
            if form.validate_on_submit():
                if checkExists(form.name.data, parent=request.form.get('parent')):
                    flash("Project name already exists.")
                    return
                else:
                    if request.form.get('group'):
                        addProject(form, parent=request.form.get('parent'), group=request.form.get('group'))                    
                    else:
                        addProject(form, parent)
            else:
                flash_errors(form.errors.items())
        else:
            form = ProjectForm()
            if form.validate_on_submit():   
                if checkExists(form.name.data):
                    flash("Project name already exists.")
                    return
                else:
                    if request.form.get('group'):
                        addProject(form, group=request.form.get('group'))                    
                    else:
                        addProject(form) 
            else:
                flash_errors(form.errors.items())      
    elif request.method == 'GET':
        if request.args.get('parent'):
            if request.form.get('group'):
                parent = current_user.group.projects.get(name=request.args.get('parent'))
            else:
                parent = current_user.projects.get(name=request.args.get('parent'))
            form = SubForm()   
            return render_template('new_project.html', form=form, parent=parent)
        else:
            form = ProjectForm()
            return render_template('new_project.html', form=form)            

@app.route('/account/aws', methods=['GET', 'POST'])
@login_requred
def aws():
    form = AWSForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if verifyAWS(form.keyID.data, form.accessKey.data):
                awsLogin = AWS(keyID=form.keyID.data, accessKey=form.accessKey.data)
                current_user.aws = awsLogin
                current_user.save()
                return redirect(url_for('account'))
            else:
                flash('aws credentials not valid.')
    return render_template('aws.html', form=form)

@app.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    form = ProjectForm()
    processLive = False
    if current_user.pid:
        try:
            os.kill(current_user.pid, 0)
            processLive = True
        except OSError:
            processLive = False
    if request.method == 'GET':
        project = current_user.projects.get(id=request.args.get('id'))
        if request.args.get('sub'):
            sub = project.subs.get(id=request.args.get('sub'))
        return render_template('project.html', project=project, sub=sub, form=form)
    elif request.method == 'POST':
        if request.form.get('action') == 'delete':
            if request.form.get('sub'):
                sub = User.objects(username=current_user.username).update_one(pull__projects__subs__name=request.form.get('name'))
            else:
                project = User.objects(username=current_user.username).update_one(pull__projects__name=request.form.get('name'))
            return redirect(url_for('account'))
        if form.validate_on_submit():
            if urlparse(form.url.data).path:
                if request.form.get('sub'):
                    parent = current_user.projects.get(name=request.form.get('name'))
                    project = parent.subs.get(name=request.form.get('sub'))
                else:
                    project = current_user.projects.get(name=request.form.get('name'))
                project.url = form.url.data
                project.steps = []
                for step in form.steps.data:
                    project['steps'].append(Step(action=step['step'], workdir=step['workdir']))
                current_user.save()
                if processLive:
                    subprocess.Popen(['buildbot', 'reconfig'], cwd=os.path.join('/build', current_user.username))
                else:
                    subprocess.Popen(['buildbot', 'start'], cwd=os.path.join('/build', current_user.username))                    
            else:
                flash('URL is not valid.')
        else:
            flash_errors(form.errors.items())
        return redirect('/project?name=' + request.form.get('name'))

@app.route('/account/masterlog', methods=['GET'])
@login_required
def masterLog():
    with open(os.path.join('/build', current_user.username, 'twistd.log')) as f:
        payload = f.readlines()[-100:]
    def logGenerator():
        for line in payload:
            yield line
    return Response(logGenerator(), mimetype='text/plain')

@app.route('/api/builders/<path:path>', methods=['GET'])
@login_required
def builders(path):
    port = sum([current_user.port_offset, 20000])
    r = requests.get(urlparse.urljoin('127.0.0.1', str(port), '/json', path))
    return(r)

@app.route('/api/force/<builder>', methods=['GET'])
@login_required
def force(builder):
    port = sum([current_user.port_offset, 20000])
    r = requests.get(urlparse.urljoin('127.0.0.1', str(port), '/builders', builder, 'force'))
    return(r)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    for user in User.objects:
        directory = os.path.join('/build', user.username)
        if len(user.projects) > 0:
            p = subprocess.Popen(['buildbot', 'start'], cwd=directory)
            user.pid = p.pid
            user.save()
    app.run(host='0.0.0.0')
