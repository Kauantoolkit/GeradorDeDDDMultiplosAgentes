from fastapi import FastAPI
from services.shipping.application import CreateAddress, UpdateShipping
app = FastAPI()
@app.post('/api/addresses')
def create_address(request: Request):
    return CreateAddress().execute()
@app.get('/api/addresses')
def get_addresses(request: Request):
    return Address().execute()
@app.post('/api/shippings')
def create_shipping(request: Request):
    return UpdateShipping().execute()
@app.get('/api/shippings')
def get_shippings(request: Request):
    return Shipping().execute()
@app.post('/api/shippings')
def update_shipping(request: Request, shipping_id: int):
    return UpdateShipping().execute(shipping_id)