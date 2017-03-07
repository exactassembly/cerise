from datetime import datetime

from .app import db
from .project.models import Step, SubProject, Project
from .group.models import AWS, Token, Referral, Group
from .user.models import User

class Token(db.Document):
    token = db.StringField()
    created = db.DateTimeField(default=datetime.now())
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 86400}
        ]
    }



 




