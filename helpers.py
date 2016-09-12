def create_master(user):
    directory = os.path.join('/build', user.username)
    try:
        os.mkdir(directory)
    except:
        pass
    c = ConfigParser()
    c.read(os.path.join(os.getcwd(), 'conf/default.conf'))
    c.set('main', 'user', user.username)
    with open(directory + '/user.conf', 'w') as f:
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

def verifyAWS(awsID, awsKey):
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

def checkExists(projName, parent=None):
if group:
    if parent:
        if current_user.group.projects.subs.get(projName) > 0:
            return True
        else:
            return False
    else:
        if current_user.group.projects.get(projName) > 0:
            return True
        else:
            return False
else:

def addProject(form, parent=None, group=None):
    if parent:
        newProject = SubProject(name=form.name.data)
    else:
        newProject = Project(name=form.name.data)               
    newProject.url = form.url.data
    newProject.steps = []
    for step in form.steps.data:
        newProject['steps'].append(Step(action=step['step'], workdir=step['workdir']))
    newProject.save()
    if group:
        if parent:
            current_user.group.projects.get(id=parent).subs.append(newProject)                    
        else:
            current_user.group.projects.append(newProject)
        current_user.group.save() 
        directory = os.path.join('/build', '_'.join(current_user.group.name.split()))
        if len(current_user.group.projects) > 0 and processLive: # reconfig
            subprocess.Popen(['buildbot', 'reconfig'], cwd=directory)            
        else: # otherwise start buildbot first time
            p = subprocess.Popen(['buildbot', 'start'], cwd=directory)  
            current_user.group.pid = p.pid
            current_user.group.save()           
    else:
        if parent:
            current_user.projects.get(id=parent).subs.append(newProject)                    
        else:
            current_user.projects.append(newProject)    
        current_user.save()
        directory = os.path.join('/build', current_user.username)
        if len(current_user.projects) > 0 and processLive: # reconfig
            subprocess.Popen(['buildbot', 'reconfig'], cwd=directory)            
        else: # otherwise start buildbot first time
            p = subprocess.Popen(['buildbot', 'start'], cwd=directory)  
            current_user.pid = p.pid
            current_user.save()