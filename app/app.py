from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')
db = MongoEngine(app)

def init_masters():
    for group in Group.objects:
        if len(group.projects) > 0:
            p = subprocess.Popen(['buildbot', 'start'], cwd=group.directory)
            group.pid = p.pid
            group.save()

init_masters()
