class Step(db.EmbeddedDocument):
    action = db.StringField(max_length=255)
    workdir = db.StringField(max_length=255)

class SubProject(db.EmbeddedDocument):
    id = db.ObjectIdField(required=True, default=lambda: ObjectId())
    name = db.StringField(max_length=255)
    url = db.StringField(max_length=255)
    steps = db.EmbeddedDocumentListField(Step, max_length=25)

class Project(db.EmbeddedDocument):
    name = db.StringField(max_length=255)
    url = db.StringField(max_length=255)
    subs = db.EmbeddedDocumentListField(SubProject, max_length=25)
    steps = db.EmbeddedDocumentListField(Step, max_length=25)