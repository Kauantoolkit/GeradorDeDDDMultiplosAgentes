from fastapi import FastAPI
from services.product_service.application.use_cases import CreateProductUseCase
app = FastAPI()
@app.post('/api/products', response_model=ProductDto)
def create_product(product: ProductDto):
    use_case = CreateProductUseCase(product)
    return use_case.execute()
