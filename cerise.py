from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import Security, MongoEngineUserDatastore, UserMixin, \
    RoleMixin, login_required    
from urllib.parse import urlparse
import boto3
app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')

db = MongoEngine(app)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)

user_datastore = MongoEngineUserDatastore(db, User)
security = Security(app, user_datastore)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spinup', methods=['POST'])
@login_required
def spinup():
    parse = urlparse(request.form['repo'])
    if parse['scheme'] and parse.['netloc']:
        GIT_REPO = request.form['repo']
    if len(request.form['token'].split()) == 1 and request.form['token'].isalnum():
        GIT_TOKEN = request.form['token']
    if 

@app.route('/buildlight')
@login_required
def buildlight():

