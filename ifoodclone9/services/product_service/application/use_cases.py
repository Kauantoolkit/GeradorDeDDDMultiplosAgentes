from services.product_service.domain import Product
from pydantic import BaseModel
class CreateProductUseCase:
    def __init__(self, product: Product):
        self.product = product
    def execute(self):
        # Criação do produto
        product.save()
        return product
