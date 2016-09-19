from bson.objectid import ObjectId
from uuid import uuid4

def create_master(group):
    directory = os.path.join('/build', '_'.join(group.name.split()))
    try:
        os.mkdir(directory)
    except:
        pass
    c = ConfigParser()
    c.read(os.path.join(os.getcwd(), 'conf/default.conf'))
    c.set('main', 'group', group.id)
    with open(directory + '/group.conf', 'w') as f:
        c.write(f)
    subprocess.call(['ln', '-s', os.path.join(os.getcwd(), 'conf/caiman.cfg'), os.path.join(directory, 'master.cfg')])
    subprocess.call(['buildbot', 'create-master'], cwd=directory)

def flash_errors(formErrors):
    for field, errors in formErrors:
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

def verify_aws(awsID, awsKey):
    client = boto3.client(
        'iam',
        aws_access_key_id=ID,
        aws_secret_access_key=awsKey
    )
    try:
        client.get_user()
        return True
    except ClientError:
        return False

def check_exists(projName, parent=None):
    if parent:
        if group.projects.subs.get(projName) > 0:
            return True
        else:
            return False
    else:
        if group.projects.get(projName) > 0:
            return True
        else:
            return False

def process_live(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def load_group(user, group):
    if user.self_group.id == group:
        return user.self_group
    elif ObjectId(user.id) in Group.objects.get(id=group):
        return Group.objects.get(id=group)
    else:
        raise ValueError('User does not have access to group.')

def add_project(group, parent=None):
    group = load_group(current_user, group)
    if check_exists(form.name.data, parent):
        raise ValueError('Project name already exists.')
    if parent:
        newProject = SubProject(name=form.name.data)
    else:
        newProject = Project(name=form.name.data)               
    newProject.url = form.url.data
    newProject.steps = []
    for step in form.steps.data:
        newProject['steps'].append(Step(action=step['step'], workdir=step['workdir']))
    if parent:
        group.projects.get(name=parent).subs.append(newProject)                    
    else:
        group.projects.append(newProject)
    group.save() 
    directory = os.path.join('/build', '_'.join(group.name.split()))
    if len(group.projects) > 0 and process_live(group.pid): # reconfig
        subprocess.Popen(['buildbot', 'reconfig'], cwd=directory)            
    else: # otherwise start buildbot first time
        p = subprocess.Popen(['buildbot', 'start'], cwd=directory)  
        group.pid = p.pid
        group.save()           

def get_project(id, group):
    group = load_group(current_user, group)
    project = group.projects.get(id=id)
    return project 

def update_project(id, group, sub=None):
    group = load_group(current_user, group)
    project = group.projects.get(id=id)
    if sub:
        project = project.subs.get(id=sub)
    project.url = form.url.data
    project.steps = []
    for step in form.steps.data:
        p['steps'].append(Step(action=step['step'], workdir=step['workdir']))
    group.save()
    directory = os.path.join('/build', '_'.join(group.name.split()))    
    if processLive:
        subprocess.Popen(['buildbot', 'reconfig'], cwd=directory)
    else:
        subprocess.Popen(['buildbot', 'start'], cwd=directory)                    

def delete_project(id, group, sub=None):
    group = load_group(current_user, group)
    project = group.projects.get(id=id)
    if sub:
        project.update(pull__subs__id=sub)
    else:
        group.update(pull__projects=p)
    group.save()

def register_user(form):
    user = User(username=form.username.data, email=form.email.data)
    user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
    if form.type.data == 'ref' and form.group.data and form.ref.data:
        user.type = 'unpaid'
        add_to_group(user, form.group.data, form.ref.data)
    else:
        if form.type.data == 'group':
            user.type = 'group'
        elif form.type.data == 'individual':
            user.type = 'individual'
        group = Group(name=current_user.username)
        group.port_offset = randint(1, 2000)
        group.save()        
        user.self_group = group
        user.save()
        group.users.append(user)
        group.save()
        user.save()
        create_master(group)

def add_to_group(user, group, ref):
    group = Group.objects.get(id=group)
    if ref in group.referrals:
        user.groups.append(group)
        user.save()
        group.users.append(user)
        group.save()
    else:
        raise ValueError('Referral not valid.')

def generate_referral(user, group):
    group = load_group(user, group)
    group.referrals.append(key=uuid4().hex)
    Token(token=uuid4().hex).save()

def validate_referral(group, key, token):
    if Token.objects.get(token=token):
        Token.objects.get(token=token).delete()
        group = Group.objects.get(id=group)
        if group.referrals.get(key=key):
            return True
        else:
            return False
    else:
        return False
