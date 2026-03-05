import React from 'react';
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
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default AgentCard;
