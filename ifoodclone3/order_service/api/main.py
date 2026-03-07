from fastapi import FastAPI
from order_service.api.routes import router

app = FastAPI()

app.include_router(router)