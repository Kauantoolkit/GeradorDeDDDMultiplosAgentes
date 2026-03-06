from fastapi import FastAPI
from users.application.use_cases import CreateUserUseCase
app = FastAPI()
@app.post('/api/users', response_model=User)
def create_user(user: User):
    use_case = CreateUserUseCase(user)
    use_case.execute()
    return user