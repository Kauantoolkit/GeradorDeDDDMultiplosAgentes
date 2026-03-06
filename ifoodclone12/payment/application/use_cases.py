from payment.domain.entities import Payment
class CreatePaymentUseCase:
    def __init__(self, payment: Payment):
        self.payment = payment
    def execute(self):
        # logic to create payment
        pass
