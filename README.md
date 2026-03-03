# Agentes Code Generator

Sistema de automação com agentes AI para geração de microserviços DDD.

## 🚀 Novidade: Frontend React com WebSocket

Agora você pode usar uma interface visual para acompanhar a execução dos agentes em tempo real!

## 📋 Requisitos

- Python 3.11+
- Node.js 18+
- Ollama instalado e configurado

## 🛠️ Instalação

### 1. Backend (API)

```
bash
# Instale as dependências Python
pip install -r requirements.txt
```

### 2. Frontend (React + Vite)

```
bash
cd frontend
npm install
```

## ▶️ Execução

### Terminal 1 - Backend API

```
bash
# Windows
start_api.bat

# Ou manualmente
python -m uvicorn api.server:app --reload --port 8000
```

### Terminal 2 - Frontend

```
bash
# Windows
start_frontend.bat

# Ou manualmente
cd frontend
npm run dev
```

### Acesse o Frontend

Abra seu navegador em: **http://localhost:5173**

## 🔌 Conexões

- **API REST**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws/{client_id}
- **Frontend**: http://localhost:5173
- **Documentação API**: http://localhost:8000/docs

## 📊 Funcionalidades do Frontend

1. **Formulário de Requisitos**: Interface para inserir os requisitos do projeto
2. **Timeline em Tempo Real**: Acompanhe cada agente sendo executado
3. **Status Visual**: Cores indicam status (pendente, executando, sucesso, erro)
4. **Score de Validação**: Veja o score de cada validação
5. **Resultado Final**: Display claro de sucesso ou erro

## 🏗️ Arquitetura

```
agentesCodeGenerator/
├── api/
│   ├── __init__.py
│   └── server.py          # FastAPI + WebSocket server
├── frontend/              # React + Vite
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── hooks/         # Custom hooks (WebSocket)
│   │   ├── App.jsx        # App principal
│   │   └── index.css      # Estilos
│   └── package.json
├── agents/                # Agentes AI
├── domain/                # Entidades DDD
├── infrastructure/        # Infraestrutura
└── README.md
```

## 💻 Uso via Terminal (Original)

```
bash
# Modo interativo
python main.py --interactive

# Com requisitos direto
python main.py --requirements "Criar um sistema de e-commerce"
```

## 🔧 Configurações

### Modelo Ollama

Edite o arquivo `api/server.py` ou use o formulário do frontend para selecionar o modelo.

Modelos disponíveis:
- llama3.2
- llama3.1
- llama3
- mistral
- codellama

### Banco de Dados

Configure no formulário:
- PostgreSQL
- MySQL
- MongoDB
- SQLite

## 📝 Licença

MIT
