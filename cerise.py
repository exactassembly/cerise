from flask import Flask, request, render_template, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension
import os, subprocess, requests

from app.app import *
from app.models import *
from app.forms import *
from app.helpers import *

login_manager = LoginManager()
login_manager.init_app(app)

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
    ref = {'group': request.args.get('group'), 'ref': request.args.get('key'), 'token': request.args.get('token') }
    if current_user.is_authenticated:
        if ref['group'] and ref['key'] and ref['token']:
            try:
                consume_token(ref['token'])
                group = load_group(current_user, ref['group'])
                group.add_to_group(current_user)
            except ValueError as e:
                return(e)
        return redirect(url_for('index'))
    if request.method == 'POST' and form.validate_on_submit():
        user = User.objects.get(username__iexact=form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            if form.group.data and form.ref.data:
                try:
                    consume_token(ref['token'])
                    group = load_group(current_user, ref['group'])
                    group.add_to_group(current_user)
                except ValueError as e:
                    return(e)
            user.authenticated = True
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', title='login', form=form, rForm=rForm, ref=ref)

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if not User.objects(username=form.username.data):
        if form.validate_on_submit():
            user = register_user(form)
            login_user(user)
            return redirect(url_for('account'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    groups = current_user.get_groups()
    if current_user.self_group:
        if not current_user.self_group.aws:
            return redirect(url_for('aws')) # require user to offer AWS information before accessing main UI
    return render_template('account.html', form=form, groups=groups)

@app.route('/account/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = RegisterForm()
    user = {username: current_user['username'], email: current_user['email']}
    groups = current_user.get_groups(admin=True)
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user.update_user(request.form)       
    return render_template('profile.html', rForm = form, user=user, groups=groups)

@app.route('/account/refer', methods=['POST'])
@login_required
def invite():
    group = current_user.groups.get(id=request.form.get('id'))
    referral = group.generate_referral()
    return referral

@app.route('/account/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        group = load_group(current_user, request.form.get('group'))        
        if request.form.get('parent'):
            form = SubForm()
            if form.validate_on_submit():
                try:
                    group.add_project(form, parent=request.form.get('parent')) 
                except ValueError as e:
                    flash(e)                   
            else:
                flash_errors(form.errors.items())
        else:
            form = ProjectForm()
            if form.validate_on_submit():   
                try:
                    group.add_project(form) 
                except ValueError as e:
                    flash(e)
            else:
                flash_errors(form.errors.items())    
        return render_template('new_project.html', form=form)  
    elif request.method == 'GET':
        if request.args.get('parent'):
            if request.form.get('group'):
                group = load_group(current_user, request.args.get('group'))                        
                parent = group.projects.get(name=request.args.get('parent'))
            else:
                parent = current_user.projects.get(name=request.args.get('parent'))
            form = SubForm()   
            return render_template('new_project.html', form=form, parent=parent)
        else:
            form = ProjectForm()
            return render_template('new_project.html', form=form)            

@app.route('/account/aws', methods=['GET', 'POST'])
@login_required
def aws():
    form = AWSForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if verify_aws(form.keyID.data, form.accessKey.data):
                aws = AWS(keyID=form.keyID.data, accessKey=form.accessKey.data)
                current_user.self_group.aws = aws
                current_user.self_group.save()
                return redirect(url_for('account'))
            else:
                flash('aws credentials not valid.')
    return render_template('aws.html', form=form)

@app.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    form = ProjectForm()
    if request.method == 'GET':
        group = load_group(current_user, request.args.get('group'))        
        try:
            project = group.get_project(request.args.get('project'))
        except ValueError as e:
            flash(e)
        if request.args.get('sub'):
            sub = project.subs.get(id=request.args.get('sub'))
        return render_template('project.html', project=project, sub=sub, form=form)
    elif request.method == 'POST':
        group = load_group(current_user, request.form.get('group'))                
        if request.form.get('action') == 'delete':
            if request.form.get('sub'):
                group.delete_project(request.form.get('project'), request.form.get('sub'))
            else:
                group.delete_project(request.form.get('project'))
            return redirect(url_for('account'))
        if form.validate_on_submit():
            if urlparse(form.url.data).path:
                if request.form.get('sub'):
                    group.update_project(request.form.get('project'), form, request.form.get('sub'))
                else:
                    group.update_project(request.form.get('project'), form)
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
    for group in Group.objects:
        directory = os.path.join('/build', '_'.join(group.name.split()))
        if len(group.projects) > 0:
            p = subprocess.Popen(['buildbot', 'start'], cwd=directory)
            group.pid = p.pid
            group.save()
    app.run(host='0.0.0.0')
