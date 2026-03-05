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
            {result.error_code && (
              <p>
                <strong>Código:</strong> {result.error_code}
              </p>
            )}
            {result.error_id && (
              <p>
                <strong>Error ID:</strong> {result.error_id} (use este ID para suporte)
              </p>
            )}
            {result.error && (
              <p>
                <strong>Erro:</strong> {result.error}
              </p>
            )}
            {result.exception_type && (
              <p>
                <strong>Tipo da exceção:</strong> {result.exception_type}
              </p>
            )}
            {result.context && Object.keys(result.context).length > 0 && (
              <div className="result-debug-block">
                <strong>Contexto:</strong>
                <pre>{JSON.stringify(result.context, null, 2)}</pre>
              </div>
            )}
            {result.hints && result.hints.length > 0 && (
              <div className="result-debug-block">
                <strong>Como investigar:</strong>
                <ul>
                  {result.hints.map((hint, index) => (
                    <li key={index}>{hint}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.logs && result.logs.length > 0 && (
              <div className="result-debug-block">
                <strong>Últimos logs:</strong>
                <pre>{result.logs.join('\n')}</pre>
              </div>
            )}
            {result.stack_trace && (
              <div className="result-debug-block">
                <strong>Stack trace:</strong>
                <pre>{result.stack_trace}</pre>
              </div>
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
