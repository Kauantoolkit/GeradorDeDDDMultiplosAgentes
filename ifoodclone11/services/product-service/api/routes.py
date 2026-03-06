from fastapi import FastAPI, HTTPException
from application import CreateProduct
app = FastAPI()
@app.post('/api/products', response_model=Product)
async def create_product(product_data: Product):
    use_case = CreateProduct()
    product = use_case.execute(product_data)
    return product
