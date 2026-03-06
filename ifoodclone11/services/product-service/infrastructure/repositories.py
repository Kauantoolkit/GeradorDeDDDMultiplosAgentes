from domain import Product
from database import Database
class ProductRepository(Database):
    def create(self, product_data):
        product = Product.create(product_data)
        self.save(product)
        return product
