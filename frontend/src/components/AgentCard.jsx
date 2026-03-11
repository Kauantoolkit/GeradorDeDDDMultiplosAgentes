import React, { useState } from 'react';
import { motion } from 'framer-motion';

const AGENT_ICONS = {
  system: '⚙️',
  orchestrator: '🎯',
  executor: '✍️',
  validator: '✅',
  fix: '🔧',
  rollback: '↩️',
  docker_test: '🐳'
};

const AGENT_NAMES = {
  system: 'Sistema',
  orchestrator: 'Orquestrador',
  executor: 'Executor',
  validator: 'Validador',
  fix: 'Correção',
  rollback: 'Rollback',
  docker_test: 'Docker Test'
};

function AgentCard({ agent, status, message, score, details, lastUpdateAt }) {
  const [showDetails, setShowDetails] = useState(false);
  const isActive = status === 'starting' || status === 'running';
  const isCompleted = status === 'completed';
  const isFailed = status === 'failed';
  const isRejected = status === 'rejected' || status === 'warning';

  const getCardClass = () => {
    if (isActive) return 'active';
    if (isCompleted) return 'completed';
    if (isFailed) return 'failed';
    if (isRejected) return 'rejected';
    return '';
  };

  // Extract input/output from details
  const inputData = details?.input;
  const outputData = details?.output;
  const hasIoData = inputData || outputData;

  return (
    <motion.div
      className={`agent-card ${getCardClass()}`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="agent-icon">
        {AGENT_ICONS[agent] || '🤖'}
      </div>

      <div className="agent-content">
        <div className="agent-header">
          <span className="agent-name">{AGENT_NAMES[agent] || agent}</span>
          <span className={`agent-status ${status}`}>
            {isActive && <span className="loading-spinner" />}
            {status}
          </span>
        </div>

        <p className="agent-message">{message}</p>

        {lastUpdateAt && (
          <p className="agent-timestamp">Última atualização: {new Date(lastUpdateAt).toLocaleTimeString()}</p>
        )}

        {score !== undefined && (
          <div className="agent-details">
            <div className="score-display">
              <span>Score:</span>
              <div className="score-bar">
                <div
                  className={`score-fill ${score < 0.5 ? 'low' : score < 0.8 ? 'medium' : ''}`}
                  style={{ width: `${score * 100}%` }}
                />
              </div>
              <span>{(score * 100).toFixed(0)}%</span>
            </div>
          </div>
        )}

        {/* Input/Output Display */}
        {hasIoData && (
          <div className="agent-io">
            <button 
              className="io-toggle-btn"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? '▼ Ocultar' : '▶ Ver Detalhes I/O'}
            </button>
            
            {showDetails && (
              <div className="io-content">
                {inputData && (
                  <div className="io-section input-section">
                    <h4>📥 INPUT (Recebido)</h4>
                    <pre>{JSON.stringify(inputData, null, 2)}</pre>
                  </div>
                )}
                
                {outputData && (
                  <div className="io-section output-section">
                    <h4>📤 OUTPUT (Gerado)</h4>
                    <pre>{JSON.stringify(outputData, null, 2)}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {details && (
          <div className="agent-details">
            {details.files && (
              <p>Arquivos: {details.files.length}</p>
            )}
            {details.feedback && (
              <p>Feedback: {details.feedback}</p>
            )}
            {details.error && (
              <p style={{ color: 'var(--danger)' }}>Erro: {details.error}</p>
            )}
            {details.diagnostics?.phase && (
              <p>Fase: {details.diagnostics.phase}</p>
            )}
            {details.diagnostics?.task_id && (
              <p>Task: {details.diagnostics.task_id}</p>
            )}
            {/* Show detailed errors in diagnostics */}
            {details.diagnostics?.detailed_errors && details.diagnostics.detailed_errors.length > 0 && (
              <div className="diagnostic-errors">
                <p style={{ color: 'var(--warning)', fontWeight: 600, marginTop: '0.5rem' }}>
                  Erros identificados:
                </p>
                {details.diagnostics.detailed_errors.map((err, idx) => (
                  <p key={idx} style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    <span style={{ color: 'var(--warning)' }}>{err.service}:</span>{' '}
                    <span style={{ color: 'var(--danger)' }}>{err.type}</span>{' '}
                    {err.message?.slice(0, 50)}
                    {err.missing_dependency && (
                      <span style={{ color: 'var(--secondary)' }}> → Instalar: {err.missing_dependency}</span>
                    )}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default AgentCard;
