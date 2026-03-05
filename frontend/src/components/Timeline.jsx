import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AgentCard from './AgentCard';

function Timeline({ agents, isActive, eventLogs = [] }) {
  // Define a ordem dos agentes na timeline
  const agentOrder = ['system', 'orchestrator', 'executor', 'validator', 'fix', 'docker_test', 'rollback'];

  // Filtra apenas agentes que receberam alguma mensagem
  const activeAgents = agentOrder.filter(agent =>
    agents[agent] && (agents[agent].status !== 'pending' || isActive)
  );

  if (activeAgents.length === 0) {
    return (
      <div className="timeline-section">
        <div className="timeline-header">
          <h2>Execução dos Agentes</h2>
        </div>
        <div className="empty-state">
          <div className="empty-state-icon">⏳</div>
          <h3>Aguardando Início</h3>
          <p>Preencha os requisitos e clique em "Gerar Projeto"</p>
        </div>
      </div>
    );
  }

  return (
    <div className="timeline-section">
      <div className="timeline-header">
        <h2>Execução dos Agentes</h2>
        {isActive && (
          <span className="agent-status running">
            <span className="loading-spinner" />
            Em execução
          </span>
        )}
      </div>

      <div className="timeline">
        <AnimatePresence>
          {activeAgents.map((agent) => (
            <AgentCard
              key={agent}
              agent={agent}
              status={agents[agent].status}
              message={agents[agent].message}
              score={agents[agent].score}
              details={agents[agent].details}
              lastUpdateAt={agents[agent].lastUpdateAt}
            />
          ))}
        </AnimatePresence>
      </div>

      {eventLogs.length > 0 && (
        <div className="event-log-panel">
          <h3>Últimos eventos (debug rápido)</h3>
          <ul>
            {eventLogs.slice(0, 8).map((event) => (
              <li key={event.id}>
                <span className="event-log-time">{new Date(event.at).toLocaleTimeString()}</span>
                <span className="event-log-kind">{event.kind}</span>
                <span className="event-log-message">
                  {event.content?.message || event.content?.status || 'evento sem mensagem'}
                </span>
                {event.content?.error_code && (
                  <span className="event-log-error">code={event.content.error_code}</span>
                )}
                {event.content?.error_id && (
                  <span className="event-log-error">id={event.content.error_id}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Timeline;
