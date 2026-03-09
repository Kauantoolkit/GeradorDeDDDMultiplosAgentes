import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';

function InvoiceRepositoryList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [newItem, setNewItem] = useState({ nome: '' });
  
  useEffect(() => {
    loadItems();
  }, []);
  
  async function loadItems() {
    try {
      setLoading(true);
      const data = await ApiService.getInvoiceRepositorys();
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  
  async function handleCreate(e) {
    e.preventDefault();
    try {
      await ApiService.createPayment(newItem);
      setShowForm(false);
      setNewItem({ nome: '' });
      loadItems();
    } catch (err) {
      alert('Erro ao criar: ' + err.message);
    }
  }
  
  async function handleDelete(id) {
    if (!confirm('Tem certeza que deseja excluir?')) return;
    try {
      await ApiService.deleteInvoiceRepository(id);
      setItems(items.filter(item => item.id !== id));
    } catch (err) {
      alert('Erro ao excluir: ' + err.message);
    }
  }
  
  if (loading) return <div className="loading">Carregando...</div>;
  if (error) return <div className="error">Erro: {error}</div>;
  
  return (
    <div className="crud-container">
      <h1>InvoiceRepositorys</h1>
      
      <button onClick={() => setShowForm(!showForm)} className="btn-create">
        {showForm ? 'Cancelar' : 'Novo'}
      </button>
      
      {showForm && (
        <form onSubmit={handleCreate} className="crud-form">
          <input
            type="text"
            placeholder="Nome"
            value={newItem.nome}
            onChange={(e) => setNewItem({ ...newItem, nome: e.target.value })}
            required
          />
          <button type="submit" className="btn-save">Salvar</button>
        </form>
      )}
      
      <table className="crud-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.nome || item.name || 'N/A'}</td>
              <td>
                <button onClick={() => handleDelete(item.id)} className="btn-delete">
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {items.length === 0 && (
        <p className="empty">Nenhum InvoiceRepository_lower encontrado</p>
      )}
    </div>
  );
}

export default InvoiceRepositoryList;
