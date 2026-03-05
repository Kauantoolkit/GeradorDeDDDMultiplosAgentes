from services.product_service.application.dtos import ProductDto
from services.product_service.domain import Product
def map_product(product: Product) -> ProductDto:
    return ProductDto(id=product.id, name=product.name, price=product.price)
