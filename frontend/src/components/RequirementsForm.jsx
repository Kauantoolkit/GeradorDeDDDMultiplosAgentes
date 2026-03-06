import React, { useState } from 'react';
import { motion } from 'framer-motion';

function RequirementsForm({ onSubmit, isGenerating }) {
  const [requirements, setRequirements] = useState('');
  const [model, setModel] = useState('llama3.2');
  const [output, setOutput] = useState('generated');
  const [framework, setFramework] = useState('python-fastapi');
  const [database, setDatabase] = useState('postgresql');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!requirements.trim()) return;

    onSubmit({
      requirements,
      model,
      output,
      framework,
      database
    });
  };

  return (
    <motion.div 
      className="requirements-form"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="form-header">
        <h2>Novo Projeto</h2>
        <p>Descreva os requisitos do seu projeto de microserviços</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group full-width">
            <label htmlFor="requirements">Requisitos do Projeto</label>
            <textarea
              id="requirements"
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
              placeholder="Ex: Criar um sistema de e-commerce com microserviços para gerenciamento de produtos, pedidos e usuários..."
              disabled={isGenerating}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="model">Modelo Ollama</label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              disabled={isGenerating}
            >
              <option value="qwen2.5-coder">Qwen 2.5 Coder</option>
              <option value="llama3.2">Llama 3.2</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="output">Diretório de Saída</label>
            <input
              id="output"
              type="text"
              value={output}
              onChange={(e) => setOutput(e.target.value)}
              placeholder="generated"
              disabled={isGenerating}
            />
          </div>

          <div className="form-group">
            <label htmlFor="framework">Framework</label>
            <select
              id="framework"
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              disabled={isGenerating}
            >
              <option value="python-fastapi">Python - FastAPI</option>
              <option value="python-flask">Python - Flask</option>
              <option value="nodejs-express">Node.js - Express</option>
              <option value="nodejs-nestjs">Node.js - NestJS</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="database">Banco de Dados</label>
            <select
              id="database"
              value={database}
              onChange={(e) => setDatabase(e.target.value)}
              disabled={isGenerating}
            >
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="mongodb">MongoDB</option>
              <option value="sqlite">SQLite</option>
            </select>
          </div>
        </div>

        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={isGenerating || !requirements.trim()}
        >
          {isGenerating ? (
            <>
              <span className="loading-spinner" />
              Gerando...
            </>
          ) : (
            <>
              🚀 Gerar Projeto
            </>
          )}
        </button>
      </form>
    </motion.div>
  );
}

export default RequirementsForm;
