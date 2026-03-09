import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';

function MemberRepositoryList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    loadItems();
  }, []);
  
  async function loadItems() {
    try {
      setLoading(true);
      const data = await ApiService.getMemberRepositorys();
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  
  async function handleDelete(id) {
    if (!confirm('Tem certeza que deseja excluir?')) return;
    try {
      await ApiService.deleteMemberRepository(id);
      setItems(items.filter(item => item.id !== id));
    } catch (err) {
      alert('Erro ao excluir: ' + err.message);
    }
  }
  
  if (loading) return <div className="loading">Carregando...</div>;
  if (error) return <div className="error">Erro: {error}</div>;
  
  return (
    <div className="crud-container">
      <h1>MemberRepositorys</h1>
      
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
        <p className="empty">Nenhum MemberRepository_lower encontrado</p>
      )}
    </div>
  );
}

export default MemberRepositoryList;
