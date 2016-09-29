from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from ..app import db
from ..group.models import Group

class User(db.Document, UserMixin):
    username = db.StringField(max_length=25)
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    groups = db.ListField(db.ReferenceField(Group, reverse_delete_rule=4), max_length=25)
    self_group = db.ReferenceField(Group, reverse_delete_rule=4)

    def update_user(self, form): # profile update view will need improvement, right now requires all fields
        if form.get('username'):
            self.username = form.get('username')
        if form.get('email'):
            self.email = form.get('email')
        if form.get('password'):
            self.password = generate_password_hash(form.get('password'), method='pbkdf2:sha1', salt_length=16)
        self.save()  

    def get_groups(self, admin=False):
        """Helper function returning a list of group objects for display in account views"""
        if admin == False:
            groups = [[{'id': x.id, 'name': x.name, 'projects': x.projects}] for x in self.groups]
        if admin == True:
            groups = [[{'id': x.id, 'name': x.name, 'projects': x.projects}] for x in self.groups if self in x.admins]
        if self.self_group:
            groups.append({'id': self.self_group.id, 'name': self.self_group.name, 'projects': self.self_group.projects})
        return groups
