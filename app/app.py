from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_envvar('CERISE_CONFIG')
db = MongoEngine(app)
