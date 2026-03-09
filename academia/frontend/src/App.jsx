import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import ApiService from './services/api';
import InstructorList from './components/InstructorList';
import ClassRepositoryList from './components/ClassRepositoryList';
import SubscriptionList from './components/SubscriptionList';
import PaymentList from './components/PaymentList';
import InvoiceList from './components/InvoiceList';
import ClassList from './components/ClassList';
import InvoiceRepositoryList from './components/InvoiceRepositoryList';
import InstructorRepositoryList from './components/InstructorRepositoryList';
import PaymentRepositoryList from './components/PaymentRepositoryList';
import MemberList from './components/MemberList';
import SubscriptionRepositoryList from './components/SubscriptionRepositoryList';
import MemberRepositoryList from './components/MemberRepositoryList';

function Home() {
  return (
    <div className="home">
      <h1>Bem-vindo ao Sistema</h1>
      <p>Selecione uma opção no menu acima</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="sidebar">
          <h2>Menu</h2>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/instructors">Instructors</Link></li>
            <li><Link to="/classrepositorys">ClassRepositorys</Link></li>
            <li><Link to="/subscriptions">Subscriptions</Link></li>
            <li><Link to="/payments">Payments</Link></li>
            <li><Link to="/invoices">Invoices</Link></li>
            <li><Link to="/classs">Classs</Link></li>
            <li><Link to="/invoicerepositorys">InvoiceRepositorys</Link></li>
            <li><Link to="/instructorrepositorys">InstructorRepositorys</Link></li>
            <li><Link to="/paymentrepositorys">PaymentRepositorys</Link></li>
            <li><Link to="/members">Members</Link></li>
            <li><Link to="/subscriptionrepositorys">SubscriptionRepositorys</Link></li>
            <li><Link to="/memberrepositorys">MemberRepositorys</Link></li>
          </ul>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/instructors" element={<InstructorList />} />
            <Route path="/classrepositorys" element={<ClassRepositoryList />} />
            <Route path="/subscriptions" element={<SubscriptionList />} />
            <Route path="/payments" element={<PaymentList />} />
            <Route path="/invoices" element={<InvoiceList />} />
            <Route path="/classs" element={<ClassList />} />
            <Route path="/invoicerepositorys" element={<InvoiceRepositoryList />} />
            <Route path="/instructorrepositorys" element={<InstructorRepositoryList />} />
            <Route path="/paymentrepositorys" element={<PaymentRepositoryList />} />
            <Route path="/members" element={<MemberList />} />
            <Route path="/subscriptionrepositorys" element={<SubscriptionRepositoryList />} />
            <Route path="/memberrepositorys" element={<MemberRepositoryList />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
