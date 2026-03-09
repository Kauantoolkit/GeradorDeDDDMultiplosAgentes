import axios from 'axios';

const ApiService = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// ==================== CLASSES (port 8002) ====================
// Classs
ApiService.getClasss = async function() {
  const response = await ApiService.get('/academia_classes/classs');
  return response.data;
};

ApiService.createClass = async function(data) {
  const response = await ApiService.post('/academia_classes/classs', data);
  return response.data;
};

ApiService.deleteClass = async function(id) {
  const response = await ApiService.delete(`/academia_classes/classs/${id}`);
  return response.data;
};

// ClassRepositorys - mapped to classes for now
ApiService.getClassRepositorys = async function() {
  const response = await ApiService.get('/academia_classes/classs');
  return response.data;
};

ApiService.deleteClassRepository = async function(id) {
  const response = await ApiService.delete(`/academia_classes/classs/${id}`);
  return response.data;
};

// ==================== MEMBERS (port 8001) ====================
// Members
ApiService.getMembers = async function() {
  const response = await ApiService.get('/academia_members/members');
  return response.data;
};

ApiService.createMember = async function(data) {
  const response = await ApiService.post('/academia_members/members', data);
  return response.data;
};

ApiService.deleteMember = async function(id) {
  const response = await ApiService.delete(`/academia_members/members/${id}`);
  return response.data;
};

// MemberRepositorys - mapped to members for now
ApiService.getMemberRepositorys = async function() {
  const response = await ApiService.get('/academia_members/members');
  return response.data;
};

ApiService.deleteMemberRepository = async function(id) {
  const response = await ApiService.delete(`/academia_members/members/${id}`);
  return response.data;
};

// Instructors - mapped to members for now
ApiService.getInstructors = async function() {
  const response = await ApiService.get('/academia_members/members');
  return response.data;
};

ApiService.deleteInstructor = async function(id) {
  const response = await ApiService.delete(`/academia_members/members/${id}`);
  return response.data;
};

// InstructorRepositorys - mapped to members for now
ApiService.getInstructorRepositorys = async function() {
  const response = await ApiService.get('/academia_members/members');
  return response.data;
};

ApiService.deleteInstructorRepository = async function(id) {
  const response = await ApiService.delete(`/academia_members/members/${id}`);
  return response.data;
};

// Subscriptions - mapped to members for now
ApiService.getSubscriptions = async function() {
  const response = await ApiService.get('/academia_members/members');
  return response.data;
};

ApiService.deleteSubscription = async function(id) {
  const response = await ApiService.delete(`/academia_members/members/${id}`);
  return response.data;
};

// SubscriptionRepositorys - mapped to members for now
ApiService.getSubscriptionRepositorys = async function() {
  const response = await ApiService.get('/academia_members/members');
  return response.data;
};

ApiService.deleteSubscriptionRepository = async function(id) {
  const response = await ApiService.delete(`/academia_members/members/${id}`);
  return response.data;
};

// ==================== PAYMENTS (port 8003) ====================
// Payments
ApiService.getPayments = async function() {
  const response = await ApiService.get('/academia_payments/payments');
  return response.data;
};

ApiService.createPayment = async function(data) {
  const response = await ApiService.post('/academia_payments/payments', data);
  return response.data;
};

ApiService.deletePayment = async function(id) {
  const response = await ApiService.delete(`/academia_payments/payments/${id}`);
  return response.data;
};

// PaymentRepositorys - mapped to payments for now
ApiService.getPaymentRepositorys = async function() {
  const response = await ApiService.get('/academia_payments/payments');
  return response.data;
};

ApiService.deletePaymentRepository = async function(id) {
  const response = await ApiService.delete(`/academia_payments/payments/${id}`);
  return response.data;
};

// Invoices - mapped to payments for now
ApiService.getInvoices = async function() {
  const response = await ApiService.get('/academia_payments/payments');
  return response.data;
};

ApiService.deleteInvoice = async function(id) {
  const response = await ApiService.delete(`/academia_payments/payments/${id}`);
  return response.data;
};

// InvoiceRepositorys - mapped to payments for now
ApiService.getInvoiceRepositorys = async function() {
  const response = await ApiService.get('/academia_payments/payments');
  return response.data;
};

ApiService.deleteInvoiceRepository = async function(id) {
  const response = await ApiService.delete(`/academia_payments/payments/${id}`);
  return response.data;
};

export default ApiService;

