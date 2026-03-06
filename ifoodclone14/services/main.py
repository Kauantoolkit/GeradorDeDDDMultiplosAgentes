from fastapi import FastAPI
from services.ifoodclone14.application import CreateOrder
app = FastAPI()
@app.post('/api/orders')
def create_order(request: Request):
    return CreateOrder().execute()