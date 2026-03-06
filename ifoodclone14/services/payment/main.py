from fastapi import FastAPI
from services.payment.application import CreatePayment, CancelPayment
app = FastAPI()
@app.post('/api/payments')
def create_payment(request: Request):
    return CreatePayment().execute()
@app.get('/api/payments')
def get_payments(request: Request):
    return Payment().execute()
@app.post('/api/payments/cancel')
def cancel_payment(request: Request):
    return CancelPayment().execute()
@app.get('/api/payments')
def get_payment(request: Request, payment_id: int):
    return Payment().execute(payment_id)