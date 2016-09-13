from bson.objectid import ObjectId

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
    if parent:
        if g.projects.subs.get(projName) > 0:
            return True
        else:
            return False
    else:
        if g.projects.get(projName) > 0:
            return True
        else:
            return False

def addProject(group, parent=None):
    if ObjectId(current_user.id) in Group.objects.get(id=group):
        g = Group.objects.get(id=group)
    else:
        raise ValueError('User does not have access to group.')
    if checkExists(projName=form.name.data, parent):
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
        g.projects.get(name=parent).subs.append(newProject)                    
    else:
        g.projects.append(newProject)
    g.save() 
    directory = os.path.join('/build', '_'.join(g.name.split()))
    if len(g.projects) > 0 and processLive: # reconfig
        subprocess.Popen(['buildbot', 'reconfig'], cwd=directory)            
    else: # otherwise start buildbot first time
        p = subprocess.Popen(['buildbot', 'start'], cwd=directory)  
        g.pid = p.pid
        g.save()           