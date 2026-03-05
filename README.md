# Agentes Code Generator

Sistema de automação com agentes de IA para geração de microserviços com abordagem DDD.

## 🌿 Estado atual das branches

- **`tentando-implementar-em-um-front`**: branch principal de uso/desenvolvimento no momento, com backend + frontend integrados (tempo real via WebSocket).
- **`main`**: branch antiga/legada, mantida como referência histórica.

> Para executar e evoluir o sistema atual, use a branch `tentando-implementar-em-um-front`.

## 🧭 Visão geral do sistema atual

O projeto hoje funciona em dois canais:

1. **Fluxo Web (recomendado)**
   - Frontend React envia requisitos para a API.
   - Backend FastAPI dispara a execução em background.
   - Atualizações dos agentes são transmitidas em tempo real por WebSocket.

2. **Fluxo CLI (modo original)**
   - Execução direta via `main.py` no terminal.
   - Mantém o mesmo núcleo de orquestração dos agentes.

## 🔁 Fluxo dos agentes (estado atual)

O ciclo executado pelo orquestrador segue este fluxo:

1. **Executor Agent**: gera os arquivos/estrutura inicial do projeto.
2. **Validator Agent**: valida arquitetura, aderência aos requisitos e consistência.
3. **Docker Test Agent**: tenta validar execução/saúde da solução gerada.
4. **Fix Agent (loop)**: quando reprovado, aplica correções e retorna para validação/testes.
5. **Resultado final**:
   - **Aprovado**: geração concluída com sucesso.
   - **Reprovado após limite de tentativas**: geração finalizada com falha e logs para diagnóstico.

## 🧩 Interface frontend (React)

A interface atual inclui:

- Formulário de requisitos do projeto.
- Seleção de modelo Ollama, framework, banco e diretório de saída.
- Timeline dos agentes em tempo real.
- Painel de eventos (debug rápido).
- Resultado final de sucesso/erro com informações de rastreio (`task_id` / `trace_id`).

## 🔌 Backend/API e comunicação

### Endpoints principais

- `GET /` → metadados da API.
- `GET /health` → healthcheck.
- `POST /api/generate` → inicia uma geração assíncrona.
- `GET /api/tasks` e `GET /api/tasks/{task_id}` → endpoints de status (estrutura básica).
- `WS /ws/{client_id}` → canal de atualização em tempo real.

### Eventos enviados no WebSocket

- `connected`
- `agent_status`
- `agent_log`
- `generation_success`
- `generation_error`

## 📋 Requisitos

- Python 3.11+
- Node.js 18+
- Ollama instalado e disponível no host

## 🛠️ Instalação

### 1) Backend

```bash
pip install -r requirements.txt
```

### 2) Frontend

```bash
cd frontend
npm install
```

## ▶️ Execução (modo web)

### Terminal 1 - API FastAPI

```bash
# Windows
start_api.bat

# Manual
python -m uvicorn api.server:app --reload --port 8000
```

### Terminal 2 - Frontend React

```bash
# Windows
start_frontend.bat

# Manual
cd frontend
npm run dev
```

Acesse: **http://localhost:5173**

## 💻 Execução via terminal (modo original)

```bash
# Interativo
python main.py --interactive

# Requisitos diretos
python main.py --requirements "Criar um sistema de e-commerce"
```

## ⚙️ Configurações suportadas no fluxo web

### Modelos Ollama

- llama3.2
- llama3.1
- llama3
- mistral
- codellama

### Frameworks

- python-fastapi
- python-flask
- nodejs-express
- nodejs-nestjs

### Bancos de dados

- postgresql
- mysql
- mongodb
- sqlite

## 📝 Licença

MIT
