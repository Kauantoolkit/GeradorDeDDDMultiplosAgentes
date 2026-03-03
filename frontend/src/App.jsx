import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import RequirementsForm from './components/RequirementsForm';
import Timeline from './components/Timeline';
import Result from './components/Result';
import useWebSocket from './hooks/useWebSocket';

// Use empty string to let Vite proxy handle it
const API_URL = '';

function App() {
  const { isConnected, lastMessage, connect } = useWebSocket();
  const [isGenerating, setIsGenerating] = useState(false);
  const [agents, setAgents] = useState({});
  const [result, setResult] = useState(null);

  // Processa mensagens recebidas via WebSocket
  useEffect(() => {
    if (!lastMessage) return;

    const { type, agent, status, message, task_id, ...data } = lastMessage;

    if (type === 'agent_status') {
      // Atualiza o estado de um agente específico
      setAgents((prev) => ({
        ...prev,
        [agent]: {
          status,
          message,
          score: data.score,
          details: data
        }
      }));
      
      // Atualiza status de geração
      if (status === 'starting') {
        setIsGenerating(true);
      } else if (status === 'completed' || status === 'failed' || status === 'rejected') {
        // Alguns agentes completam mas a geração continua
      }
    } 
    else if (type === 'generation_success') {
      setResult(lastMessage);
      setIsGenerating(false);
    }
    else if (type === 'generation_error') {
      setResult(lastMessage);
      setIsGenerating(false);
    }
    else if (type === 'connected') {
      console.log('Conectado ao servidor:', lastMessage.message);
    }
  }, [lastMessage]);

  // Envia requisição para a API
  const handleGenerate = useCallback(async (formData) => {
    try {
      setIsGenerating(true);
      setResult(null);
      setAgents({});

      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`Erro na API: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Geração iniciada:', data);
      
      // O status será atualizado via WebSocket
    } catch (error) {
      console.error('Erro ao iniciar geração:', error);
      setIsGenerating(false);
      setResult({
        type: 'generation_error',
        message: 'Erro ao conectar com o servidor',
        error: error.message
      });
    }
  }, []);

  // Limpa o estado para uma nova geração
  const handleReset = useCallback(() => {
    setAgents({});
    setResult(null);
    setIsGenerating(false);
  }, []);

  return (
    <div className="app">
      <Header 
        isConnected={isConnected} 
        onConnect={connect}
      />
      
      <main className="main-content">
        <RequirementsForm 
          onSubmit={handleGenerate}
          isGenerating={isGenerating}
        />
        
        <Timeline 
          agents={agents}
          isActive={isGenerating}
        />
        
        <Result result={result} />
        
        {result && (
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <button 
              className="btn btn-secondary"
              onClick={handleReset}
            >
              Nova Geração
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
