# TODO - Fix Agent Flow Implementation

## ✅ Concluído

### Fase 1: Criar FixAgent ✅
- [x] Criar agents/fix_agent.py
  - [x] Implementar classe FixAgent
  - [x] Receber feedback do Validator
  - [x] Corrigir os problemas identificados
  - [x] Registrar ações realizadas no log de erros

### Fase 2: Criar Log de Erros ✅
- [x] Criar agents/error_logger.py
  - [x] Implementar classe ErrorLogger
  - [x] Salvar logs em logs/agent_errors.log
  - [x] Registrar: problema, correção aplicada, resultado
  - [x] Formato estruturado para análise posterior

### Fase 3: Modificar Orchestrator ✅
- [x] Modificar agents/orchestrator.py
  - [x] Substituir Rollback por FixAgent no fluxo
  - [x] Adicionar loop de retry com Fix Agent
  - [x] Adicionar limite máximo de tentativas (max_fix_attempts)
  - [x] Integrar ErrorLogger
  - [x] Manter Rollback apenas para erros críticos (após limite de correções)

### Fase 4: Atualizar Entidades ✅
- [x] Modificar domain/entities.py
  - [x] Adicionar FIX ao AgentType enum

## Novo Fluxo de Agentes

```
┌──────────────┐
│  REQUISITOS  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  EXECUTOR   │ ◄── Gera código
│   AGENT     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  VALIDATOR  │ ◄── Valida código
│   AGENT     │
└──────┬───────┘
       │
 ┌─────┴─────┐
 │           │
 ▼           ▼
APROVADO   REPROVADO
 │           │
 ▼           ▼
SUCESSO   FIX AGENT
           (loop)
             │
       ┌─────┴─────┐
       ▼           ▼
   APROVADO    REPROVADO
       │           │
       ▼           ▼
  DOCKER TEST  ROLLBACK
  (continua)   (limite atingido)
```

## Arquivos Criados/Modificados

1. **agents/fix_agent.py** (NOVO)
   - Agente que corrige problemas identificados pelo Validator
   - Pode usar LLM para sugerir correções
   - Fallback para correções básicas

2. **agents/error_logger.py** (NOVO)
   - Registra erros em logs/agent_errors.log
   - Mantém histórico de correções
   - Fornece análise de problemas comuns

3. **agents/orchestrator.py** (MODIFICADO)
   - Novo fluxo com Fix Agent
   - Loop de correção até aprovação ou limite
   - Rollback apenas após falha do Fix Agent

4. **domain/entities.py** (MODIFICADO)
   - Adicionado AgentType.FIX

## Configuração

O número máximo de tentativas de correção pode ser configurado:
```
python
orchestrator = OrchestratorAgent(llm_provider, max_fix_attempts=3)
```

## Logs de Erros

Os erros são salvos em formato JSON em `logs/agent_errors.log`:
- Problemas identificados
- Correções aplicadas
- Resultados de cada tentativa
- Problemas comuns (para análise)
