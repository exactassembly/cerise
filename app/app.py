from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)

db = MongoEngine(app)

