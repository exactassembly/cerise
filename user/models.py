from flask_login import UserMixin
from cerise import db

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