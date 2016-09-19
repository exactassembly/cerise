from cerise import db
from flask_login import UserMixin
from flask_wtf import Form
from wtforms import StringField, PasswordField, validators, FieldList, FormField
from wtforms import Form as wtForm
from datetime import datetime

class Token(db.Document):
    token = db.StringField()
    created = db.DateTimeField(default=datetime.now())
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 86400}
        ]
    }



 




