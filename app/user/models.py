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

    def update_user(self):
        if request.form.get('username'):
            current_user['username'] = request.form.get('username')
        if request.form.get('email'):
            current_user['email'] = request.form.get('email')
        if request.form.get('password'):
            current_user['password'] = request.form.get('password')  
        current_user.save()  

    def get_groups(self, admin=False):
        if admin == False:
            groups = [[{'id': x.id, 'name': x.name, 'projects': x.projects}] for x in current_user.groups]
        if admin == True:
            groups = [[{'id': x.id, 'projects': x.projects}] for x in current_user.groups if current_user in x.admins]
        if current_user.self_group:
            groups.append({'id': current_user.self_group.id, 'projects': current_user.self_group.projects})
