import React from 'react';

function Header({ isConnected, onConnect }) {
  return (
    <header className="header">
      <div className="header-logo">
        <div className="logo-icon">🤖</div>
        <h1>Agentes Code Generator</h1>
      </div>
      
      <div className="connection-status">
        <span className={`status-dot ${isConnected ? 'connected' : ''}`} />
        <span>{isConnected ? 'Conectado' : 'Desconectado'}</span>
        {!isConnected && (
          <button 
            className="btn btn-secondary" 
            onClick={onConnect}
            style={{ marginLeft: '1rem', padding: '0.5rem 1rem' }}
          >
            Reconectar
          </button>
        )}
      </div>
    </header>
  );
}

export default Header;
