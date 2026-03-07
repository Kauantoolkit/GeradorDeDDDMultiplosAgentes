# Plano de Correções - Agentes de Geração

## Status Atual das Correções

### ✅ Concluídas/Alta Prioridade:
1. Docker Compose Sobrescrito - executor_agent.py não gera mais docker-compose.yml por serviço
2. PlaceholderReplacer - Aplicado em todos os métodos de geração
3. Syntax Validation - Arquivos com erro são removidos
4. Validação Duplicada - Rota duplicada movida para Validator
5. Frontend Genérico - Usa entity_name dinamicamente
6. Validação de Entidades - _check_service_entity_consistency implementado
7. Dependencies Duplicada - centralizado

### ⏳ Pendentes (a corrigir):
5. Retry Logic Duplicada
6. Busca Flexível
7. Níveis de Log
8. Mensagens
9. Logger Unificado

---

## Correções a Implementar

### 1. Retry Logic Duplicada (Média Prioridade)

**Problema:**
- Executor tem retry interno (max_generation_attempts = 10)
- FixAgent tem retry para correções  
- Orchestrator tem loop de retry
- Duplicação de lógica

**Correção Proposta:**
- Remover retry interno do Executor (deve falhar rapidamente)
- Manter retry no FixAgent para correções determinísticas
- Manter retry no Orchestrator para o fluxo geral

**Arquivos afetados:**
- agents/executor_agent.py - remover retry loop
- agents/fix_agent.py - manter retry
- agents/orchestrator.py - já está correto

---

### 2. Busca Flexível como Solução de Contorno (Média Prioridade)

**Problema:**
- `read_file_flexible()` e `find_file_with_flexible_search()` são usadas extensivamente
- Isso mascara o problema real: nomes de arquivos inconsistentes entre agentes

**Correção Proposta:**
- Aplicar normalização de nomes no momento da geração (Executor)
- Criar utilitário de nomenclatura padrão
- Adicionar validação de nomes no Validator

**Arquivos afetados:**
- infrastructure/file_manager.py
- agents/executor_agent.py
- agents/validator_agent.py
- agents/fix_agent.py

---

### 3. Níveis de Log Inconsistentes (Baixa Prioridade)

**Problema:**
- Alguns usam `logger.error()` para problemas recuperáveis
- Outros usam `logger.warning()` para erros críticos

**Correção Proposta:**
- ERROR: Falhas que impedem continuação
- WARNING: Problemas recuperáveis
- INFO: Progresso normal

**Arquivos afetados:**
- Múltiplos arquivos

---

### 4. Mensagens em Português e Inglês (Baixa Prioridade)

**Problema:**
- Mensagens misturam português e inglês

**Correção Proposta:**
- Padronizar para português para interface
- Inglês para logs técnicos

**Arquivos afetados:**
- Múltiplos arquivos

---

### 5. Logger Duplicado (Baixa Prioridade)

**Problema:**
- Dois sistemas de logging (agent_logger.py e error_logger.py)
- Funcionalidades sobrepostas

**Correção Proposta:**
- Unificar em um único sistema
- Manter apenas agent_logger com capacidade de erros
- error_logger pode ser módulo de utilidade

**Arquivos afetados:**
- agents/agent_logger.py
- agents/error_logger.py

---

## Ordem de Implementação Sugerida

1. Retry Logic Duplicada (#1)
2. Busca Flexível (#2)
3. Logger Unificado (#5) - mais impactante
4. Níveis de Log (#3)
5. Mensagens (#4)

---

## Detalhamento Técnico

### Retry Logic

**ExecutorAgent** - deve falhar rapidamente, não fazer retry:
```python
# Mudar de:
for attempt in range(1, self.max_generation_attempts + 1):
    # ... retry logic
    
# Para:
# Receber attempts do orchestrator, fazer apenas 1 tentativa
# Retornar erro rapidamente se falhar
```

**FixAgent** - retry para correções determinísticas é OK:
- Manter retry interno para correções determinísticas de dependências
- Mas usar retry externo para correções via LLM

### Busca Flexível

**Criar normalizador de nomes:**
```python
# infrastructure/name_normalizer.py
def normalize_file_path(path: str, service_name: str, domain: str) -> str:
    """Normaliza caminho de arquivo para padrão do projeto."""
    # Substitui hífen por underscore
    # Garante consistência com estrutura DDD
    return path.replace('-', '_')
```

**Validação no Validator:**
- Verificar se arquivos seguem padrão de nomenclatura
- Reportar inconsistências como issues

