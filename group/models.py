class AWS(db.EmbeddedDocument):
    keyID = db.StringField(max_length=255)
    accessKey = db.StringField(max_length=255)

class Referral(db.EmbeddedDocument):
    key = db.StringField()
    created = db.DateTimeField(default=datetime.now())
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 86400}
        ]
    }

class Group(db.Document):
    name = db.StringField(max_length=50)
    port_offset = db.IntField()
    aws = db.EmbeddedDocumentField(AWS)
    pid = db.IntField()
    projects = db.EmbeddedDocumentListField(Project, max_length=50)
    users = db.ListField(db.ReferenceField('User'), max_length=100)
    referrals = db.EmbeddedDocumentListField(Referral, max_length=100)

    def create_master(self):
        directory = os.path.join('/build', '_'.join(self.name.split()))
        try:
            os.mkdir(directory)
        except:
            pass
        c = ConfigParser()
        c.read(os.path.join(os.getcwd(), 'conf/default.conf'))
        c.set('main', 'group', self.id)
        with open(directory + '/group.conf', 'w') as f:
            c.write(f)
        subprocess.call(['ln', '-s', os.path.join(os.getcwd(), 'conf/caiman.cfg'), os.path.join(directory, 'master.cfg')])
        subprocess.call(['buildbot', 'create-master'], cwd=directory)

    def add_to_group(self, user):
        if self.referrals.get(key=key):
            user.groups.append(group)
            user.save()
            self.users.append(user.id)
            self.save()
        else:
            raise ValueError('Referral not valid.')

    def generate_referral(self):
        self.referrals.append(key=uuid4().hex)
        Token(token=uuid4().hex).save()

    def get_project(self, id):
        project = self.projects.get(id=id)
        return project 

    def update_project(id, sub=None):
        project = self.projects.get(id=id)
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
        
    def add_project(self, parent=None):
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
            self.projects.get(name=parent).subs.append(newProject)                    
        else:
            self.projects.append(newProject)
        self.save() 
        directory = os.path.join('/build', '_'.join(self.name.split()))
        if len(self.projects) > 0 and process_live(self.pid): # reconfig
            subprocess.Popen(['buildbot', 'reconfig'], cwd=directory)            
        else: # otherwise start buildbot first time
            p = subprocess.Popen(['buildbot', 'start'], cwd=directory)  
            self.pid = p.pid
            self.save()   

    def delete_project(self, id, sub=None):
        project = self.projects.get(id=id)
        if sub:
            project.update(pull__subs__id=sub)
        else:
            self.update(pull__projects=p)
        self.save()

    def process_live(self):
        try:
            os.kill(self.pid, 0)
            return True
        except OSError:
            return False

    def check_exists(self, parent=None):
        if parent:
            if self.projects.subs.get(projName) > 0:
                return True
            else:
                return False
        else:
            if self.projects.get(projName) > 0:
                return True
            else:
                return False

