from products.domain.entities import Product
class CreateProductUseCase:
    def __init__(self, product: Product):
        self.product = product
    def execute(self):
        # logic to create product
        pass
