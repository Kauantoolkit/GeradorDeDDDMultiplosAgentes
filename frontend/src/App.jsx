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
  const [waitingForDatabase, setWaitingForDatabase] = useState(false);
  const [databaseInfo, setDatabaseInfo] = useState(null);
  const [agents, setAgents] = useState({});
  const [result, setResult] = useState(null);
  const [eventLogs, setEventLogs] = useState([]);

  const appendEventLog = useCallback((kind, content) => {
    const entry = {
      id: `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      at: new Date().toISOString(),
      kind,
      content
    };

    setEventLogs((prev) => [entry, ...prev].slice(0, 25));
  }, []);

  // Processa mensagens recebidas via WebSocket
  useEffect(() => {
    if (!lastMessage) return;

    const { type, agent, status, message, task_id, ...data } = lastMessage;

    appendEventLog(type || 'unknown', {
      agent,
      status,
      task_id,
      message,
      error_code: data.error_code,
      error_id: data.error_id
    });

    if (type === 'agent_status' || type === 'agent_log') {
      // Atualiza o estado de um agente específico
      setAgents((prev) => ({
        ...prev,
        [agent]: {
          status,
          message,
          score: data.score,
          details: data,
          lastUpdateAt: new Date().toISOString()
        }
      }));

      if (status === 'starting') {
        setIsGenerating(true);
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
    else if (type === 'database_creation_required') {
      setWaitingForDatabase(true);
      setDatabaseInfo({
        message: lastMessage.message,
        databaseUrls: lastMessage.database_urls || {},
        projectPath: lastMessage.project_path,
        taskId: lastMessage.task_id
      });
      setIsGenerating(false);
    }
    else if (type === 'connected') {
      console.log('Conectado ao servidor:', lastMessage.message);
    }
  }, [lastMessage, appendEventLog]);

  // Envia requisição para a API
  const handleGenerate = useCallback(async (formData) => {
    try {
      setIsGenerating(true);
      setResult(null);
      setAgents({});
      setEventLogs([]);

      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detail = errorData?.detail;
        const detailMessage = typeof detail === 'string' ? detail : detail?.message;
        throw new Error(`Erro na API (${response.status}): ${detailMessage || response.statusText}`);
      }

      const data = await response.json();
      console.log('Geração iniciada:', data);
      appendEventLog('generation_started', {
        task_id: data.task_id,
        status: data.status,
        message: data.message
      });

      // O status será atualizado via WebSocket
    } catch (error) {
      console.error('Erro ao iniciar geração:', error);
      setIsGenerating(false);
      const fallbackResult = {
        type: 'generation_error',
        message: 'Erro ao conectar com o servidor',
        error: error.message,
        hints: [
          'Confirme se backend e frontend estão iniciados.',
          'Teste GET /health para validar se a API está disponível.',
          'Confira o console do navegador e logs/api_server.log.'
        ]
      };
      setResult(fallbackResult);
      appendEventLog('generation_error', fallbackResult);
    }
  }, [appendEventLog]);

  // Limpa o estado para uma nova geração
  const handleReset = useCallback(() => {
    setAgents({});
    setResult(null);
    setIsGenerating(false);
    setEventLogs([]);
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
          eventLogs={eventLogs}
        />

        <Result result={result} />

        {waitingForDatabase && databaseInfo && (
          <div style={{
            padding: '2rem',
            background: '#fff3cd',
            border: '1px solid #ffc107',
            borderRadius: '8px',
            marginTop: '2rem',
            textAlign: 'center'
          }}>
            <h3 style={{ color: '#856404', marginBottom: '1rem' }}>
              🗄️ Criação de Bancos de Dados Necessária
            </h3>
            <p style={{ color: '#856404', marginBottom: '1.5rem' }}>
              {databaseInfo.message || 'Por favor, crie os bancos de dados abaixo no pgAdmin antes de continuar'}
            </p>
            
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              alignItems: 'center'
            }}>
              {Object.entries(databaseInfo.databaseUrls || {}).map(([name, url]) => (
                <div key={name} style={{
                  background: 'white',
                  padding: '1rem',
                  borderRadius: '4px',
                  width: '100%',
                  maxWidth: '600px',
                  textAlign: 'left'
                }}>
                  <strong style={{ color: '#333' }}>{name}:</strong>
                  <code style={{
                    display: 'block',
                    marginTop: '0.5rem',
                    padding: '0.5rem',
                    background: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '0.9rem',
                    wordBreak: 'break-all'
                  }}>
                    {url}
                  </code>
                </div>
              ))}
              
              {Object.keys(databaseInfo.databaseUrls || {}).length === 0 && (
                <p style={{ color: '#856404' }}>
                  Nenhuma URL de banco encontrada. Verifique o console para detalhes.
                </p>
              )}
            </div>
            
            <button
              onClick={async () => {
                try {
                  const response = await fetch(`/api/continue/${databaseInfo.taskId}`, {
                    method: 'POST'
                  });
                  if (response.ok) {
                    setWaitingForDatabase(false);
                    setIsGenerating(true);
                  }
                } catch (err) {
                  console.error('Erro ao continuar:', err);
                }
              }}
              style={{
                marginTop: '1.5rem',
                padding: '0.75rem 2rem',
                fontSize: '1rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              ✅ Já criei os bancos - Continuar
            </button>
          </div>
        )}

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
