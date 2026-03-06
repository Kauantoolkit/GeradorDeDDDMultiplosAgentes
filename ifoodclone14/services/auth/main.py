from fastapi import FastAPI
from services.auth.application import Login, Register
app = FastAPI()
@app.post('/api/login')
def login(request: Request):
    return Login().execute()
@app.post('/api/register')
def register(request: Request):
    return Register().execute()
@app.get('/api/users')
def get_users(request: Request):
    return User().execute()
@app.get('/api/users')
def get_user(request: Request, user_id: int):
    return User().execute(user_id)