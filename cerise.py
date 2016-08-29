from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_mongoengine import MongoEngine
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
import os, boto3, subprocess, requests
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
    directory = os.path.join('/build' + user.username)
    try:
        os.mkdir(directory)
    except OSError as e:
        if e[0] = 17:   # path exists
            pass
    c = ConfigParser()
    c.read(os.path.join(os.getcwd(), 'conf/default.conf'))
    c.set('main', 'user', user.username)
    with open(directory + '/user.conf', 'w') as f:
        c.write(f)
    subprocess.call(['ln', '-s', os.path.join(os.getcwd(), 'conf/caiman.cfg'), os.path.join(directory, 'master.cfg')])
    subprocess.call(['buildbot', 'create-master'], cwd=directory)

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
            return redirect(url_for('account'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = ProjectForm()
    projects = current_user['projects']
    try:
        os.kill(current_user.pid, 0)
        processLive = True
    except OSError:
        processLive = False
    if request.method == 'POST':
        if form.validate_on_submit():
            if not current_user.projects.filter(name=form.name.data):
                if urlparse(form.gitrepo.data).path:                
                    newProject = Project(name=form.name.data)
                    newProject.gitrepo = form.gitrepo.data
                    newProject.steps = []
                    directory = os.path.join('/build', current_user.username)
                    for step in form.steps.data:
                        newProject['steps'].append(Step(action=step['step'], workdir=step['workdir']))
                    current_user.projects.append(newProject)
                    current_user.save()
                    if len(current_user.projects) > 1 and processLive: # reconfig
                        subprocess.Popen(['buildbot', 'reconfig'], cwd=directory)            
                    else: # otherwise start buildbot first time
                        p = subprocess.Popen(['buildbot', 'start'], cwd=directory)  
                        current_user.pid = p.pid
                        current_user.save()              
                else:
                    flash("URL is not valid.")
            else:
                flash("Project name already exists.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(u"Error in the %s field - %s" % (
                        getattr(form, field).label.text,
                        error
                    ))
    return render_template('account.html', form=form, projects=projects, processLive=processLive)

@app.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    form = ProjectForm()
    try:
        os.kill(current_user.pid, 0)
        processLive = True
    except OSError:
        processLive = False
    if request.method == 'GET':
        currentProject = request.args.get('name')
        project = current_user.projects.get(name=currentProject)
        return render_template('project.html', project=project, form=form)
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            project = User.objects(username=current_user.username).update_one(pull__projects__name=request.form.get('name'))
            return redirect(url_for('account'))
        if form.validate_on_submit():
            if urlparse(form.gitrepo.data).path:
                project = current_user.projects.get(name=request.form.get('name'))
                project.gitrepo = form.gitrepo.data
                project.steps = []
                for step in form.steps.data:
                    project['steps'].append(Step(action=step['step'], workdir=step['workdir']))
                if form.subs.data:
                    project.sourcerepos = []
                    for sub in form.subs.data:
                        project['sourcerepos'].append(Repo(name=sub['name'], url=sub['url']))
                current_user.save()
                if processLive:
                    subprocess.Popen(['buildbot', 'reconfig'], cwd=os.path.join('/build', current_user.username)
                else:
                    subprocess.Popen(['buildbot', 'start'], cwd=os.path.join('/build', current_user.username)                    
            else:
                flash('URL is not valid.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(u"Error in the %s field - %s" % (
                        getattr(form, field).label.text,
                        error
                    ))
        return redirect('/project?name=' + request.form.get('name'))

@app.route('/account/masterlog', methods=['GET'])
@login_required
def masterLog():
    with open(os.path.join('/build', current_user.username, 'twistd.log')) as f:
        payload = f.read()
        return payload   

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

@app.route('/api/log/<str:builder>/<int:buildnumber>')
@login_required
def log(buildnumber):
    port = sum([current_user.port_offset, 20000])
    j = requests.get(url.parse.urljoin('127.0.0.1', str(port), '/json/builders', builder, 'builds', buildnumber), params={'as_text' : '1'}).json()
    payload = {}
    for i in j['steps']:
        r = requests.get(i['logs'][1])
        payload[i['name']] = r
    return render_template('log.html', payload=payload)

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
