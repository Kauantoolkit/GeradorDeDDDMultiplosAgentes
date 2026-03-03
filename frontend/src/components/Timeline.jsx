import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AgentCard from './AgentCard';

function Timeline({ agents, isActive }) {
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
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default Timeline;
