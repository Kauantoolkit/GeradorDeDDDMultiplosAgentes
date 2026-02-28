# Sistema de Automação com Agentes para Geração de Microserviços DDD

## Visão Geral

Este sistema utiliza agentes AI para automatizar a geração de código de microserviços baseados em arquitetura DDD (Domain-Driven Design).

### Arquitetura dos Agentes

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                         │
│                  (Coordena todo o fluxo)                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│  EXECUTOR AGENT    │         │  VALIDATOR AGENT   │
│  (Gera código)     │         │  (Valida resultado) │
└─────────┬───────────┘         └─────────┬───────────┘
          │                               │
          │         ┌─────────────┐       │
          └────────►│   ROLLBACK  │◄──────┘
                    │   AGENT     │
                    │ (Desfaz)    │
                    └─────────────┘
```

### Fluxo de Execução

1. **Usuário** → Envia requisitos via CLI
2. **Executor Agent** → Gera estrutura DDD + microserviços
3. **Validator Agent** → Compara código gerado com requisitos
4. **Se reprovar** → **Rollback Agent** → Remove arquivos gerados
5. **Se aprovar** → Código final disponibilizado

---

## Pré-requisitos

1. **Python 3.11+**
2. **Ollama** instalado e configurado localmente
   - Download: https://ollama.ai
   - Modelo recomendado: `llama3.2`

### Instalação do Ollama (Windows)

```
powershell
# Via winget (recomendado)
winget install Ollama.Ollama

# Ou baixe diretamente de: https://github.com/ollama/ollama/releases
```

### Após instalar o Ollama

```
bash
# Iniciar o serviço Ollama
ollama serve

# Em outro terminal, baixar o modelo
ollama pull llama3.2

# Verificar modelos instalados
ollama list
```

---

## Instalação

```
bash
# 1. Clone ou baixe o projeto

# 2. Crie um ambiente virtual (opcional mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o Ollama
# Certifique-se de que o Ollama está rodando:
# ollama serve
# E o modelo está instalado:
# ollama pull llama3.2
```

---

## Uso

### Modo Interativo

```
bash
python main.py --interactive
```

### Via Linha de Comando

```
bash
# Exemplo básico
python main.py --requirements "Criar um sistema de e-commerce com microserviços para produtos, pedidos e usuários"

# Especificando diretório de saída
python main.py --requirements "..." --output meu-projeto

# Especificando modelo
python main.py --requirements "..." --model llama3.2

# Modo verboso (debug)
python main.py --requirements "..." --verbose
```

---

## Estrutura do Projeto Gerado

O sistema gera uma estrutura DDD completa:

```
generated/
├── services/
│   ├── products/           # Microserviço de produtos
│   │   ├── domain/         # Camada de domínio
│   │   │   ├── __init__.py
│   │   │   ├── product_entities.py
│   │   │   ├── product_value_objects.py
│   │   │   └── product_aggregates.py
│   │   ├── application/   # Camada de aplicação
│   │   │   ├── use_cases.py
│   │   │   ├── dtos.py
│   │   │   └── mappers.py
│   │   ├── infrastructure/ # Camada de infraestrutura
│   │   │   ├── repositories.py
│   │   │   └── database.py
│   │   ├── api/           # Camada de API
│   │   │   ├── routes.py
│   │   │   ├── controllers.py
│   │   │   └── schemas.py
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── orders/            # Microserviço de pedidos
│   └── users/             # Microserviço de usuários
├── docker-compose.yml
└── README.md
```

---

## Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```
env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OUTPUT_DIRECTORY=generated
DEFAULT_FRAMEWORK=python-fastapi
DEFAULT_DATABASE=postgresql
LOG_LEVEL=INFO
```

---

## Como Funciona

### Executor Agent
- Analisa os requisitos
- Identifica microserviços necessários
- Gera estrutura DDD completa
- Cria arquivos de código

### Validator Agent
- Compara código gerado com requisitos
- Verifica estrutura DDD
- Identifica problemas
- Aprova ou reprova

### Rollback Agent
- Remove arquivos criados
- Limpa diretórios
- Gera relatório de rollback

---

## Exemplos de Requisitos

```
"Criar sistema de gestão de tarefas com microserviços para projetos, tarefas e comentários"

"Criar API de delivery com restaurantes, pedidos e entregadores"

"Sistema de biblioteca digital com livros, autores, gêneros e empréstimos"
```

---

## Troubleshooting

### Ollama não conecta
```
bash
# Verifique se o Ollama está rodando
ollama serve

# Teste a conexão
curl http://localhost:11434/api/tags
```

### Erro de dependências
```
bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

---

## Licença

MIT
