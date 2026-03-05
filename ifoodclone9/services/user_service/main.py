from fastapi import FastAPI
from services.user_service.application.use_cases import CreateUserUseCase
from services.user_service.application.dtos import UserDto
app = FastAPI()
@app.post('/api/users', response_model=UserDto)
def create_user(user: UserDto):
    use_case = CreateUserUseCase(user)
    return use_case.execute()
