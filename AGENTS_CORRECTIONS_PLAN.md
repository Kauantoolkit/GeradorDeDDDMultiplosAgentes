# Plano de Correções - Inconsistências dos Agentes

## Visão Geral
Este documento lista todas as inconsistências identificadas nos agentes de geração e o plano de correção.

---

## 1. Validação Duplicada de Rotas
**Arquivos afetados:** `executor_agent.py`, `validator_agent.py`

**Problema:** 
- `_validate_generated_files()` em Executor verifica rotas duplicadas
- `_check_duplicate_routes()` em Validator também verifica
- Duplicação de lógica

**Correção:** Remover validação de rotas do Executor, manter apenas no Validator

---

## 2. PlaceholderReplacer Não Usado Consistentemente
**Arquivos afetados:** `executor_agent.py`

**Problema:** 
- PlaceholderReplacer existe mas não é aplicado em todos os métodos de geração
- Alguns métodos geram código com placeholders que não são verificados
- `_generate_entity`, `_generate_value_objects`, etc. usam f-strings diretamente

**Correção:** Aplicar PlaceholderReplacer em todos os métodos de geração após a geração do conteúdo

---

## 3. Geração de Frontend Genérico
**Arquivos afetados:** `executor_agent.py` - método `_generate_frontend`

**Problema:**
- Gera frontend hardcoded com entidade "User"
- Não adapta ao contexto do requisito (ex: "Order", "Product")
- validator verifica se frontend existe mas não valida qualidade

**Correção:**
- Extrair nome da entidade do requisito
- Gerar frontend dinamicamente baseado na entidade

---

## 4. Docker Compose Sobrescrito
**Arquivos afetados:** `executor_agent.py`, `docker_test_agent.py`

**Problema:**
- Executor gera `docker-compose.yml` para cada microserviço
- DockerTestAgent gera `docker-compose.yml` unificado no diretório raiz
- O compose unificado sobrescreve os individuais

**Correção:**
- Executor NÃO deve gerar docker-compose.yml (apenas Dockerfile por serviço)
- DockerTestAgent gera o compose unificado
- Adicionar flag para controlar isso

---

## 5. Arquivos com Erro de Syntax Ainda São Criados
**Arquivos afetados:** `executor_agent.py`

**Problema:**
- `_validate_generated_files()` detecta erro de syntax via `ast.parse()`
- Apenas loga o erro mas não impede que o arquivo seja mantido
- Arquivos inválidos são criados e mantidos

**Correção:**
- Adicionar método para remover arquivos com erro de syntax
- Ou não registrar arquivo como "criado com sucesso" se tem erro

---

## 6. Validação de Dependencies Duplicada
**Arquivos afetados:** `executor_agent.py`, `validator_agent.py`, `fix_agent.py`

**Problema:**
- Executor: `_ensure_runtime_dependencies()` garante dependências mínimas
- Validator: `_check_service_email_dependency()` verifica dependências de email
- FixAgent: `_fix_emailstr_dependencies()` adiciona dependências

**Correção:**
- Centralizar verificação de dependências em um único lugar
- Remover duplicações

---

## 7. Níveis de Log Inconsistentes
**Arquivos afetados:** Múltiplos arquivos

**Problema:**
- Alguns usam `logger.error()` para problemas recuperáveis
- Outros usam `logger.warning()` para erros críticos
- Inconsistência na severidade

**Correção:**
- Definir padrões:
  - ERROR: Falhas que impedem continuação
  - WARNING: Problemas recuperáveis
  - INFO: Progresso normal

---

## 8. Mensagens em Português e Inglês
**Arquivos afetados:** Múltiplos arquivos

**Problema:**
- Mensagens misturam português e inglês
- Ex: "Arquivo criado" vs "File created"

**Correção:**
- Padronizar para um idioma (recomendado: português para interface, inglês para logs técnicos)

---

## 9. Retry Logic Duplicada
**Arquivos afetados:** `executor_agent.py`, `fix_agent.py`, `orchestrator.py`

**Problema:**
- Executor tem retry interno para geração
- FixAgent tem retry para correções
- Orchestrator tem loop de retry

**Correção:**
- Manter retry apenas no Orchestrator
- Executor e FixAgent devem retornar erro e deixar retry por conta do Orchestrator

---

## 10. Busca Flexível como Solução de Contorno
**Arquivos afetados:** `file_manager.py`, `validator_agent.py`, `fix_agent.py`

**Problema:**
- `read_file_flexible()` e `find_file_with_flexible_search()` são usadas extensivamente
- Isso mascara o problema real: nomes de arquivos inconsistentes entre agentes

**Correção:**
- Aplicar normalização de nomes no momento da geração (Executor)
- Garantir que todos os agentes usem o mesmo padrão de nomenclatura
- Remover gradualmente a dependência de busca flexível

---

## 11. Validação de Entidades Incompleta
**Arquivos afetados:** `validator_agent.py`

**Problema:**
- `_check_service_entity_consistency()` verifica se entidades existem
- Mas não verifica se todas as classes referenciadas estão definidas

**Correção:**
- Adicionar verificação de classes não definidas
- Verificar referências circulares

---

## 12. Logger Duplicado
**Arquivos afetados:** `agent_logger.py`, `error_logger.py`

**Problema:**
- Dois sistemas de logging com funcionalidades sobrepostas
- agent_logger para execuções
- error_logger para erros

**Correção:**
- Unificar em um único sistema de logging
- Manter apenas agent_logger com capacidade de erros

---

## Priorização das Correções

### Alta Prioridade (Críticas):
1. Docker Compose Sobrescrito (#4)
2. Arquivos com Erro de Syntax Criados (#5)
3. PlaceholderReplacer Não Usado (#2)

### Média Prioridade:
4. Validação Duplicada (#1, #6)
5. Retry Logic Duplicada (#9)
6. Busca Flexível (#10)

### Baixa Prioridade:
7. Níveis de Log (#7)
8. Mensagens (#8)
9. Logger Duplicado (#12)
10. Geração de Frontend (#3)
11. Validação de Entidades (#11)

---

## Status das Correções

| # | Correção | Status | Arquivo |
|---|----------|--------|---------|
| 1 | Docker Compose | Pendente | executor_agent.py, docker_test_agent.py |
| 2 | PlaceholderReplacer | Pendente | executor_agent.py |
| 3 | Syntax Validation | Pendente | executor_agent.py |
| 4 | Validação Duplicada | Pendente | executor_agent.py, validator_agent.py |
| 5 | Retry Logic | Pendente | Múltiplos |
| 6 | Busca Flexível | Pendente | file_manager.py + agentes |
| 7 | Níveis de Log | Pendente | Múltiplos |
| 8 | Mensagens | Pendente | Múltiplos |
| 9 | Logger Unificado | Pendente | agent_logger.py, error_logger.py |
| 10 | Frontend Genérico | Pendente | executor_agent.py |
| 11 | Validação Entidades | Pendente | validator_agent.py |

---

## Executando as Correções

Para cada correção, seguir o padrão:
1. Ler o arquivo afetado
2. Identificar o código específico a modificar
3. Aplicar a correção
4. Testar se possível

**Ordem sugerida:**
1. Começar por #1 (Docker Compose) - mais impactante
2. Seguir para #2 (PlaceholderReplacer)
3. Depois #3 (Syntax Validation)
4. Continuar nas demais

