from fastapi import FastAPI
from services.user_service.application.use_cases import CreateUserUseCase
from services.user_service.application.dtos import UserDTO

app = FastAPI()
@app.post('/api/users', response_model=UserDTO)
def create_user(user: UserDTO):
    use_case = CreateUserUseCase(user)
    result = use_case.execute()
    return result