import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import ApiService from './services/api';
import InvoiceRepositoryList from './components/InvoiceRepositoryList';
import MemberRepositoryList from './components/MemberRepositoryList';
import MemberList from './components/MemberList';
import SessionList from './components/SessionList';
import SessionRepositoryList from './components/SessionRepositoryList';
import InvoiceList from './components/InvoiceList';

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
            <li><Link to="/invoicerepositorys">InvoiceRepositorys</Link></li>
            <li><Link to="/memberrepositorys">MemberRepositorys</Link></li>
            <li><Link to="/members">Members</Link></li>
            <li><Link to="/sessions">Sessions</Link></li>
            <li><Link to="/sessionrepositorys">SessionRepositorys</Link></li>
            <li><Link to="/invoices">Invoices</Link></li>
          </ul>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/invoicerepositorys" element={<InvoiceRepositoryList />} />
            <Route path="/memberrepositorys" element={<MemberRepositoryList />} />
            <Route path="/members" element={<MemberList />} />
            <Route path="/sessions" element={<SessionList />} />
            <Route path="/sessionrepositorys" element={<SessionRepositoryList />} />
            <Route path="/invoices" element={<InvoiceList />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;

