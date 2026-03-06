from domain import Product, Category
from value_objects import ProductStatus
from aggregates import ProductAggregate
from events import ProductCreatedEvent
from application import UseCaseBase
class CreateProduct(UseCaseBase):
    def execute(self, product_data):
        product = Product.create(product_data)
        product.save()
        return product
