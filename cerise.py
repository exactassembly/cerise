from flask import Flask
import boto3
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spinup', methods=['POST'])
def spinup():
    GIT_REPO = request.form['repo']
    GIT_TOKEN = request.form['token']

