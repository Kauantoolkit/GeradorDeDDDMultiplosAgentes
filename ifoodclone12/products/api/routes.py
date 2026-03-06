from fastapi import FastAPI
from products.application.use_cases import CreateProductUseCase
app = FastAPI()
@app.post('/api/products', response_model=Product)
def create_product(product: Product):
    use_case = CreateProductUseCase(product)
    use_case.execute()
    return product