from datetime import datetime

from .user.models import *
from .project.models import *
from .group.models import *

class Token(db.Document):
    token = db.StringField()
    created = db.DateTimeField(default=datetime.now())
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 86400}
        ]
    }



 




