import json

from flask import Flask, request
from flask_basicauth import BasicAuth

app = Flask(__name__)

with open('credentials.json', 'r') as fh:
    credentials = json.load(fh)

app.config['BASIC_AUTH_USERNAME'] = credentials['username']
app.config['BASIC_AUTH_PASSWORD'] = credentials['password']
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

@app.route('/reg_form_data', methods=['POST'])
def reg_form_data():
    print(request.json)
    return f'Reg num: {request.json["reg_num"]}'
