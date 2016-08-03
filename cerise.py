from flask import Flask
from urllib.parse import urlparse
import boto3
app = Flask(__name__)

AWS_ACCESS_ID=""
AWS_ACCESS_KEY=""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spinup', methods=['POST'])
def spinup():
    parse = urlparse(request.form['repo'])
    if parse['scheme'] and parse.['netloc']:
        GIT_REPO = request.form['repo']
    if len(request.form['token'].split()) == 1 and request.form['token'].isalnum():
        GIT_TOKEN = request.form['token']
    if 


