# Tentativa de Rodar ifoodclone3 - Relatório de Problemas

**Data da tentativa:** 04-03-26  
**Status:** FALHA

---

## Problemas Identificados

### 1. Erro de Import nos Serviços (CRÍTICO)
**Serviços afetados:** orders, users, products

**Erro:**
```
ImportError: attempted relative import with no known parent package
```

**Causa:** 
- O arquivo `main.py` usa imports relativos: `from .api.routes import router`
- O Docker executa `python main.py` diretamente sem treating it as a package
- O `main.py` precisa ser executado como módulo ou usar imports absolutos

**Arquivos afetados:**
- `ifoodclone3/services/orders/main.py` (linha 9)
- `ifoodclone3/services/users/main.py` (linha 9)
- `ifoodclone3/services/products/main.py` (linha 9)

---

### 2. Erro nos Bancos de Dados PostgreSQL (CRÍTICO)
**Serviços afetados:** db-orders, db-users, db-products

**Erro:**
```
Error: in 18+, these Docker images are configured to store database data in a
format which is compatible with "pg_ctlcluster"...
```

**Causa:**
- O docker-compose usa a imagem `postgres` (latest - versão 18+)
- Há volumes de dados de versões anteriores do PostgreSQL
- Conflito de versão com dados existentes

**Containers afetados:**
- ifoodclone3-db-orders-1
- ifoodclone3-db-users-1
- ifoodclone3-db-products-1

---

## Estrutura dos Arquivos

### Dockerfiles (idênticos para todos os serviços)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

### Problema no Dockerfile
- O CMD executa `python main.py` diretamente
- Não há `__init__.py` configurado corretamente para imports relativos funcionarem

---

## Possíveis Soluções (não implementado - foco é documentar)

### Para erro de import:
1. Mudar para imports absolutos: `from api.routes import router`
2. Ou adicionar `__init__.py` e executar como módulo: `python -m services.orders.main`
3. Ou criar um script de entrypoint que configure o PYTHONPATH

### Para erro do PostgreSQL:
1. Remover os volumes existentes: `docker volume rm ifoodclone3_pgdata-orders`
2. Usar versão específica do PostgreSQL no docker-compose: `image: postgres:16`
3. Limpar dados antigos antes de iniciar

---

## Logs Capturados

### orders-1
```
Traceback (most recent call last):
  File "/app/main.py", line 9, in <module>
    from .api.routes import router
ImportError: attempted relative import with no known parent package
```

### users-1
```
Traceback (most recent call last):
  File "/app/main.py", line 9, in <module>
    from .api.routes import router
ImportError: attempted relative import with no known parent package
```

### products-1
```
Traceback (most recent call last):
  File "/app/main.py", line 9, in <module>
    from .api.routes import router
ImportError: attempted relative import with no known parent package
```

### db-orders-1
```
Error: in 18+, these Docker images are configured to store database data in a
format which is compatible with "pg_ctlcluster" (specifically, using
major-version-specific directory names)...
```

---

## Conclusão

O projeto **não rodou** devido a dois problemas principais:
1. **Erro de importação** - O código usa imports relativos mas é executado de forma incompatível
2. **Conflito de versão PostgreSQL** - Dados de versões anteriores causando problemas na inicialização

O foco foi mantidO em **documentar** os problemas conforme solicitado, sem refatorar o código.

