from flask_login import UserMixin
from ..app import db
from ..group.models import Group

class User(db.Document, UserMixin):
    username = db.StringField(max_length=25)
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    groups = db.ListField(db.ReferenceField(Group), max_length=25)
    self_group = db.ReferenceField(Group)

    def update_user(self, form):
        if form.get('username'):
            self.username = form.get('username')
        if form.get('email'):
            self.email = form.get('email')
        if form.get('password'):
            self.password = form.get('password')  
        self.save()  

    def get_groups(self, admin=False):
        if admin == False:
            groups = [[{'id': x.id, 'name': x.name, 'projects': x.projects}] for x in self.groups]
        if admin == True:
            groups = [[{'id': x.id, 'projects': x.projects}] for x in self.groups if self in x.admins]
        if self.self_group:
            groups.append({'id': self.self_group.id, 'projects': self.self_group.projects})
