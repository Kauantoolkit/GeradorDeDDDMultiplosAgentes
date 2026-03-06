from fastapi import FastAPI, HTTPException
from application import CreateUser
app = FastAPI()
@app.post('/api/users', response_model=User)
async def create_user(user_data: User):
    use_case = CreateUser()
    user = use_case.execute(user_data)
    return user
