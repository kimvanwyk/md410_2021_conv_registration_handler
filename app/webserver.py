import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
from pydantic import BaseModel

class Item(BaseModel):
    reg_num: int

app = FastAPI()
security = HTTPBasic()

with open('credentials.json', 'r') as fh:
    creds = json.load(fh)

@app.post('/reg_form_data')
def reg_form_data(item: Item, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != creds['username'] or credentials.password != creds['password']:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return f'Reg num: {item.reg_num}'
