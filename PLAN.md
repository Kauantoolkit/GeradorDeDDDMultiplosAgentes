# Plano de Implementação - Sistema de Logging Estruturado

## Objetivo
Melhorar a observabilidade do sistema de agentes com logging estruturado, rastreabilidade completa (trace_id, message_id) e capacidade de reproduzir fluxos apenas lendo os logs.

---

## Análise do Código Atual

### Agentes existentes:
1. **OrchestratorAgent** - Coordena o fluxo entre agentes
2. **ExecutorAgent** - Gera código baseado em requisitos
3. **ValidatorAgent** - Valida código gerado
4. **FixAgent** - Corrige problemas identificados
5. **RollbackAgent** - Desfaz mudanças
6. **DockerTestAgent** - Valida containers Docker

### Problemas identificados:
- Logs分散ados usando `loguru` sem estrutura uniforme
- Não há trace_id para correlacionarexecuções
- Não há message_id para cada comunicação entre agentes
- Logs não capturam input/output completo dos agentes
- Stack traces podem não estar sendo persistidos adequadamente

---

## Plano de Implementação

### Fase 1: Criar Módulo de Logging Estruturado (`agents/agent_logger.py`)

**Arquivo:** `agents/agent_logger.py`

**Funcionalidades:**
1. `AgentLogger` - Classe principal de logging
   - Geração de trace_id (UUID único por execução)
   - Geração de message_id (UUID único por mensagem)
   - Logging estruturado em JSON
   - Persistência em arquivo (`logs/agent_execution.log`)
   - Stack traces completos para erros

2. `AgentExecutionContext` - Contexto de execução
   - Armazena trace_id atual
   - Propaga contexto entre agentes
   - Mantém histórico de mensagens

3. Funções auxiliares:
   - `get_logger()` - Retorna instância global
   - `create_trace()` - Inicia novo trace
   - `log_agent_call()` - Log de chamada de agente

### Fase 2: Atualizar Entidades do Domínio

**Arquivo:** `domain/entities.py`

**Adicionar campos:**
- `trace_id` em: Requirement, ExecutionResult, ValidationResult
- `message_id` em: ExecutionResult (para comunicações)

### Fase 3: Instrumentar Agentes

**Arquivos a modificar:**
1. `agents/orchestrator.py` - Logging centralizado do fluxo
2. `agents/executor_agent.py` - Logging de input/output
3. `agents/validator_agent.py` - Logging de validação
4. `agents/fix_agent.py` - Logging de correções
5. `agents/rollback_agent.py` - Logging de rollback
6. `agents/docker_test_agent.py` - Logging de testes Docker

**Cada agente deve registrar:**
- Timestamp (ISO 8601)
- Nome do agente
- trace_id e message_id
- Input completo recebido
- Output completo enviado
- Tempo de execução
- Erros com stack trace completo

### Fase 4: Logging de Comunicação Inter-Agentes

**Formato do log de comunicação:**
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "trace_id": "uuid-execucao",
  "message_id": "uuid-mensagem",
  "type": "AGENT_COMMUNICATION",
  "from_agent": "ExecutorAgent",
  "to_agent": "ValidatorAgent",
  "payload": {...},
  "status": "success|failure",
  "execution_time_ms": 1500
}
```

---

## Formato do Log Estruturado

### Log de Execução de Agente
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "type": "AGENT_EXECUTION",
  "agent_name": "ExecutorAgent",
  "input": {
    "requirement": {...}
  },
  "output": {
    "files_created": [...],
    "status": "success"
  },
  "execution_time_ms": 15000,
  "error": null
}
```

### Log de Erro
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "550e8400-e29b-41d4-a716-446655440002",
  "type": "AGENT_ERROR",
  "agent_name": "ExecutorAgent",
  "error_type": "ValueError",
  "error_message": "Mensagem de erro",
  "stack_trace": "Traceback (most recent call last)...",
  "input": {...}
}
```

---

## Arquivos a Criar/Modificar

### Novos Arquivos:
1. `agents/agent_logger.py` - Módulo de logging estruturado

### Arquivos a Modificar:
1. `domain/entities.py` - Adicionar trace_id e message_id
2. `agents/orchestrator.py` - Instrumentar logging
3. `agents/executor_agent.py` - Instrumentar logging
4. `agents/validator_agent.py` - Instrumentar logging
5. `agents/fix_agent.py` - Instrumentar logging
6. `agents/rollback_agent.py` - Instrumentar logging
7. `agents/docker_test_agent.py` - Instrumentar logging

---

## Dependências
- `uuid` (biblioteca padrão)
- `json` (biblioteca padrão)
- `datetime` (biblioteca padrão)
- `traceback` (biblioteca padrão)
- `loguru` (já utilizado)

---

## Critérios de Sucesso
1. ✅ Cada execução gera um trace_id único
2. ✅ Cada comunicação entre agentes gera message_id único
3. ✅ Logs podem ser correlacionados via trace_id
4. ✅ Input/output completo de cada agente é persistido
5. ✅ Stack traces completos em caso de erros
6. ✅ Tempo de execução registrado
7. ✅ Logs em formato JSON para fácil parsing
8. ✅ Persistência em arquivo dedicado

