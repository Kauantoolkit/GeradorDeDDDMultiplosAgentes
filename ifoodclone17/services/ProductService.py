from ifoodclone17.domain import Product
from ifoodclone17.application import UseCase
class ProductService(UseCase):
    def get_products(self):
        return [Product() for _ in range(10)]
    def create_product(self):
        return Product()
