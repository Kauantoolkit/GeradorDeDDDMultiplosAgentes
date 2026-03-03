import React from 'react';
import { motion } from 'framer-motion';

function Result({ result }) {
  if (!result) return null;

  const isSuccess = result.type === 'generation_success';
  const isError = result.type === 'generation_error';

  if (!isSuccess && !isError) return null;

  return (
    <motion.div 
      className={`result-section ${isSuccess ? 'success' : 'error'}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <div className="result-header">
        <div className="result-icon">
          {isSuccess ? '🎉' : '❌'}
        </div>
        <h2 className="result-title">
          {isSuccess ? 'Projeto Gerado com Sucesso!' : 'Erro na Geração'}
        </h2>
      </div>

      <div className="result-details">
        {isSuccess ? (
          <>
            <p>
              <strong>Localização:</strong> {result.project_path || 'generated/'}
            </p>
            <p>
              <strong>Arquivos gerados:</strong> {result.files_count || 0}
            </p>
            {result.services && result.services.length > 0 && (
              <p>
                <strong>Serviços:</strong> {result.services.join(', ')}
              </p>
            )}
          </>
        ) : (
          <>
            <p>
              <strong>Mensagem:</strong> {result.message}
            </p>
            {result.error && (
              <p>
                <strong>Erro:</strong> {result.error}
              </p>
            )}
            {result.score !== undefined && (
              <p>
                <strong>Score final:</strong> {(result.score * 100).toFixed(0)}%
              </p>
            )}
          </>
        )}
      </div>
    </motion.div>
  );
}

export default Result;
