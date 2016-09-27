import os, subprocess

from ..app import db
from ..project.models import Project, Step
from configparser import ConfigParser
from datetime import datetime
from uuid import uuid4
from mongoengine.errors import DoesNotExist

class AWS(db.EmbeddedDocument):
    keyID = db.StringField(max_length=255)
    accessKey = db.StringField(max_length=255)

class Token(db.Document):
    token = db.StringField()
    created = db.DateTimeField(default=datetime.now())
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 86400}
        ]
    }

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
    port_offset = db.SequenceField()
    aws = db.EmbeddedDocumentField(AWS)
    pid = db.IntField()
    projects = db.EmbeddedDocumentListField(Project, max_length=50)
    users = db.ListField(db.ReferenceField('User'), max_length=100)
    admins = db.ListField(db.ReferenceField('User'), max_length=100)
    referrals = db.EmbeddedDocumentListField(Referral, max_length=100)
    directory = db.StringField()

    def create_master(self):
        try:
            os.mkdir(self.directory)
        except:
            pass
        c = ConfigParser()
        c.read(os.path.join(os.getcwd(), 'conf/default.conf'))
        c.set('main', 'group', str(self.id))
        with open(self.directory + '/group.conf', 'w') as f:
            c.write(f)
        subprocess.call(['ln', '-s', os.path.join(os.getcwd(), 'conf/caiman.cfg'), os.path.join(self.directory, 'master.cfg')])
        subprocess.call(['buildbot', 'create-master'], cwd=self.directory)

    def add_to_group(self, user):
        if self.referrals.get(key=key):
            user.groups.append(group)
            user.save()
            self.users.append(user.id)
            self.save()
        else:
            raise ValueError('Referral not valid.')

    def generate_referral(self):
        key = uuid4().hex
        token = uuid4().hex
        self.referrals.append(Referral(key=key))
        self.save()
        Token(token=token).save()
        return {'key': key, 'token': token}

    def get_project(self, id):
        project = self.projects.get(id=id)
        return project 

    def update_project(id, form, sub=None):
        project = self.projects.get(id=id)
        if sub:
            project = project.subs.get(id=sub)
        project.url = form.url.data
        project.steps = []
        for step in form.steps.data:
            p['steps'].append(Step(action=step['step'], workdir=step['workdir']))
        group.save()
        if processLive:
            subprocess.Popen(['buildbot', 'reconfig'], cwd=self.directory)
        else:
            subprocess.Popen(['buildbot', 'start'], cwd=self.directory)  
        
    def add_project(self, form, parent=None):
        if self.check_exists(form.name.data, parent):
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
            self.projects.get(id=parent).subs.append(newProject)                    
        else:
            self.projects.append(newProject)
        self.save() 
        if len(self.projects) > 0 and self.process_live(): # reconfig
            subprocess.Popen(['buildbot', 'reconfig'], cwd=self.directory)            
        else: # otherwise start buildbot first time
            p = subprocess.Popen(['buildbot', 'start'], cwd=self.directory)  
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
        if not self.pid:
            return False
        try:
            os.kill(self.pid, 0)
            return True
        except OSError:
            return False

    def check_exists(self, name, parent=None):
        if parent:
            try:
                self.projects.subs.get(name=name)
                return True
            except DoesNotExist:
                return False
        else:
            try:
                self.projects.get(name=name)
                return True
            except DoesNotExist:
                return False

