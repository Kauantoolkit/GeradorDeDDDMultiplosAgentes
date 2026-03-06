from fastapi import FastAPI
from payment.application.use_cases import CreatePaymentUseCase
app = FastAPI()
@app.post('/api/payments', response_model=Payment)
def create_payment(payment: Payment):
    use_case = CreatePaymentUseCase(payment)
    use_case.execute()
    return payment