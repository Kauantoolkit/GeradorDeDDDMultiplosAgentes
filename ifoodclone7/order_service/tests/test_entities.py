from domain.entities import Order, OrderItem

def test_order_creation():
    order_id = OrderId('123e4567-e89b-12d3-a456-426614174000')
    customer_id = CustomerId('123e4567-e89b-12d3-a456-426614174001')
    restaurant_id = RestaurantId('123e4567-e89b-12d3-a456-426614174002')
    item = OrderItem(product_id=UUID('123e4567-e89b-12d3-a456-426614174003'), quantity=2)
    order = Order(order_id, customer_id, restaurant_id, [item])
    assert order.order_id == order_id
    assert order.customer_id == customer_id
    assert order.restaurant_id == restaurant_id
    assert order.items == [item]
