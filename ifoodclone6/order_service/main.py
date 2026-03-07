from fastapi import FastAPI
from .api import order_router

app = FastAPI()

app.include_router(order_router)