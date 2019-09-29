import json

import requests

with open('credentials.json', 'r') as fh:
    credentials = json.load(fh)

res = requests.post('http://localhost:9003/reg_form_data',
                    auth=(credentials['username'], credentials['password']),
                    json={'reg_num': '18'}
)

res.raise_for_status()
print(res.text)
