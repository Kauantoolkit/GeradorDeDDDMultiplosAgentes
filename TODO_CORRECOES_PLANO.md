# Plano de Correções - Agente de Geração

## Status: CONCLUÍDO ✅

### Problema Original:
O agente de geração estava apresentando problemas em 2 apps gerados. Os problemas comuns identificados foram:
1. **Prompt genérico**: O prompt tinha exemplos hardcoded que influenciavam a geração
2. **Banco de dados não existe**: A validação falhava porque os bancos não existiam no PostgreSQL

---

### Alterações Realizadas:

#### 1. Prompt Genérico (`infrastructure/llm_provider.py`)
- ✅ Removidos exemplos hardcoded como "billing", "invoice", etc.
- ✅ Prompt agora é genérico - LLM decide estrutura baseada nos requisitos
- ✅ Adicionada instrução para gerar `database_urls` no JSON de resposta

#### 2. Extração de Database URLs (`agents/code_agent.py`)
- ✅ Adicionado método `_extract_database_urls()` para extrair URLs do JSON
- ✅ Modificado método `_generate_and_create_files()` para retornar parsed_data
- ✅ O agente agora retorna `database_urls` no resultado

#### 3. Entidades Atualizadas (`domain/entities.py`)
- ✅ Adicionado campo `database_urls: dict` em `ExecutionResult`
- ✅ Adicionado campo `database_urls: dict` em `ProjectGenerationResult`
- ✅ Adicionado campo `waiting_for_databases: bool` em `ExecutionResult`

#### 4. Orchestrator (`agents/orchestrator_v3.py`)
- ✅ Copia `database_urls` do generation_result para o resultado final
- ✅ Adiciona log com as URLs que usuário precisa criar
- ✅ Pausa após geração e retorna com `waiting_for_databases=True`
- ✅ Envia mensagem via WebSocket pedindo criação de bancos

#### 5. API Server (`api/server.py`)
- ✅ Adicionado variável global `pending_tasks` para armazenar tasks pendentes
- ✅ Adicionado endpoint `/api/continue/{task_id}` para continuar após criação de bancos
- ✅ Envia mensagem `database_creation_required` via WebSocket quando precisa pausar

---

## Fluxo Novo:

```
1. Usuário envia requisitos
2. CodeAgent.generate() → gera código + JSON com database_urls
3. database_urls são extraídas e salvas no resultado
4. Sistema ENVIA mensagem WebSocket: "database_creation_required"
5. Frontend mostra popup com URLs e botão "Continuar"
6. Usuário cria os bancos no pgAdmin
7. Usuário clica "Continuar" → chama /api/continue/{task_id}
8. Sistema continua com a validação
```

---

## Como Testar:

1. Iniciar a API: `uvicorn api.server:app --reload --port 8000`
2. Abrir frontend e conectar WebSocket
3. Enviar requisição de geração
4. Receber mensagem `database_creation_required` com as URLs
5. Criar os bancos no pgAdmin
6. Clicar em "Continuar" no frontend
7. Verificar se a validação continua
