# Erros Encontrados no iFood Clone 8

## Data da Execução: 05/03/2026

## Resumo da Execução

Comando executado: `docker-compose up --build`

## Erros Identificados

### 1. user_service - Falha Crítica (Container não inicia)

**Status:** ❌ ERRO

**Detalhes:**
- Container: `ifoodclone8-user_service-1`
- Status: Exited (127)
- Mensagem de erro: `/bin/sh: 1: [uvicorn,: not found`

**Causa Raiz:**
O arquivo `requirements.txt` do serviço `user_service` está incompleto. Está faltando o pacote `uvicorn` que é necessário para executar o servidor FastAPI.

**Arquivo com problema:**
- `ifoodclone8/services/user_service/requirements.txt`

**Conteúdo atual do requirements.txt:**
```
fastapi
sqlalchemy
```

**Comparação com outros serviços (corretos):**
Os outros serviços possuem o requirements.txt completo:
```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
python-dotenv>=1.0.0
```

**Dockerfile:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000']
```

O Dockerfile está correto, utilizando `uvicorn` no comando CMD, mas o pacote não está instalado porque não está no requirements.txt.

---

## Serviços Funcionando Corretamente

### 2. order_service - ✅ FUNCIONANDO

- Container: `ifoodclone8-order_service-1`
- Porta: 18002
- Status: Up
- API Docs disponível: http://localhost:18002/docs

### 3. product_service - ✅ FUNCIONANDO

- Container: `ifoodclone8-product_service-1`
- Porta: 18003
- Status: Up
- API Docs disponível: http://localhost:18003/docs

### 4. payment_service - ✅ FUNCIONANDO

- Container: `ifoodclone8-payment_service-1`
- Porta: 18004
- Status: Up
- API Docs disponível: http://localhost:18004/docs

### 5. Databases - ✅ FUNCIONANDO

Todos os bancos de dados PostgreSQL estão rodando corretamente:
- `ifoodclone8-db-user_service-1` (porta 5432)
- `ifoodclone8-db-order_service-1` (porta 5432)
- `ifoodclone8-db-product_service-1` (porta 5432)
- `ifoodclone8-db-payment_service-1` (porta 5432)

---

## Resumo

| Serviço | Status | Porta |
|---------|--------|-------|
| user_service | ❌ ERRO | 18001 (não inicia) |
| order_service | ✅ OK | 18002 |
| product_service | ✅ OK | 18003 |
| payment_service | ✅ OK | 18004 |

**Total: 1 erro crítico (user_service não inicia)**

---

## Observações Adicionais

### Front-end
- **Status:** ❌ NÃO EXISTE
- O ifoodclone8 NÃO POSSUI FRONT-END
- Apenas contém microsserviços backend (user_service, order_service, product_service, payment_service)
- Não há pasta `frontend` ou serviço de front-end no projeto

