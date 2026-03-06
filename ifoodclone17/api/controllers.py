from fastapi import FastAPI, HTTPException
from ifoodclone17.application import OrderService
from ifoodclone17.infrastructure import Database
app = FastAPI()
@app.get('/api/orders')
def get_orders():
    return OrderService().get_orders()
@app.post('/api/orders')
def create_order():
    return OrderService().create_order()
@app.get('/api/products')
def get_products():
    return ProductService().get_products()
@app.post('/api/products')
def create_product():
    return ProductService().create_product()
@app.get('/api/login')
def login_user():
    return UserService().login_user()
@app.post('/api/login')
def login_user():
    return UserService().login_user()
if __name__ == '__main__':
    app.run()
