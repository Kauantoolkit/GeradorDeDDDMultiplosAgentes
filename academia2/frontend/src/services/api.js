import axios from 'axios';

const ApiService = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Member endpoints
export const memberService = {
  create: (data) => ApiService.post('/membership_service/members', data),
  gets: () => ApiService.get('/membership_service/members'),
};

// Invoice endpoints
export const invoiceService = {
  create: (data) => ApiService.post('/payment_service/invoices', data),
  gets: () => ApiService.get('/payment_service/invoices'),
};

// Session endpoints
export const sessionService = {
  create: (data) => ApiService.post('/training_service/sessions', data),
  gets: () => ApiService.get('/training_service/sessions'),
};

export default ApiService;

