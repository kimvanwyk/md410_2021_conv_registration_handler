from flask import Flask, request
app = Flask(__name__)

@app.route('/reg_form_data', methods=['POST'])
def reg_form_data():
    print(request.json)
    return f'Reg num: {request.json["reg_num"]}'
