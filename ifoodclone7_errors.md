# Erros encontrados ao rodar ifoodclone7

## Resumo
Todos os 3 serviços (orders, users, products) falharam ao iniciar devido a erros de **importação circular** (circular import).

---

## Erro 1: orders service

### Mensagem de Erro:
```
Traceback (most recent call last):
  File "/app/main.py", line 9, in <module>
    from api.routes import router
  File "/app/api/routes.py", line 4, in <module>
    from domain import OrderRepository
  File "/app/domain/__init__.py", line 1, in <module>
    from domain import Order, Product, User
ImportError: cannot import name 'Order' from partially initialized module 'domain' (most likely due to a circular import)
```

### Causa Raiz:
- O arquivo `domain/__init__.py` tenta importar `Order`, `Product`, `User` de `domain`
- Esses arquivos existem em `domain/orders_entities.py`, `domain/products_entities.py`, `domain/users_entities.py`
- Porém o `__init__.py` está mal configurado, tentando importar diretamente de "domain" em vez de ".orders_entities"

### Arquivos Envolvidos:
- `/app/domain/__init__.py`
- `/app/domain/orders_entities.py`

---

## Erro 2: users service

### Mensagem de Erro:
```
Traceback (most recent call last):
  File "/app/main.py", line 9, in <module>
    from api.routes import router
  File "/app/api/routes.py", line 12, in <module>
    from application.use_cases import (
  File "/app/application/use_cases.py", line 8, in <module>
    from domain import User
  File "/app/domain/__init__.py", line 4, in <module>
    from .users_aggregates import *
  File "/app/domain/users_aggregates.py", line 9, in <module>
    from . import User
ImportError: cannot import name 'User' from partially initialized module 'domain' (most likely due to a circular import)
```

### Causa Raiz:
- `users_aggregates.py` tenta importar `User` de `domain` (via `from . import User`)
- Mas `domain/__init__.py` está tentando importar de `users_aggregates`
- Isso cria um ciclo: domain/__init__ -> users_aggregates -> domain

### Arquivos Envolvidos:
- `/app/domain/__init__.py`
- `/app/domain/users_aggregates.py`

---

## Erro 3: products service

### Mensagem de Erro:
```
Traceback (most recent call last):
  File "/app/main.py", line 9, in <module>
    from api.routes import router
  File "/app/api/routes.py", line 12, in <module>
    from application.use_cases import (
  File "/app/application/use_cases.py", line 8, in <module>
    from domain import Product
  File "/app/domain/__init__.py", line 4, in <module>
    from .products_aggregates import *
  File "/app/domain/products_aggregates.py", line 9, in <module>
    from . import Product
ImportError: cannot import name 'Product' from partially initialized module 'domain' (most likely due to a circular import)
```

### Causa Raiz:
- Mesmo problema que users: `products_aggregates.py` tenta importar `Product` de `domain`
- Enquanto `domain/__init__.py` importa de `products_aggregates`
- Criando ciclo de importação

### Arquivos Envolvidos:
- `/app/domain/__init__.py`
- `/app/domain/products_aggregates.py`

---

## Problemas Adicionais Identificados

### 1. Estrutura de diretórios inconsistente
- `orders/domain/orders_entities.py` define entidade `User` (deveria ser `Order`)
- Isso indica confusão na estrutura do código

### 2. domain/__init__.py mal configurado (orders)
```python
from domain import Order, Product, User  # ERRADO
# Deveria ser:
from .orders_entities import Order
from .products_entities import Product  
from .users_entities import User
```

### 3. Arquivo duplicado/inconsistente
- `orders/infrastructure/infrastucture/` (com "t" a mais) - possivelmente typo

### 4. Frontend não está configurado para servir
- Existe arquivo HTML estático em `services/orders/static/index.html`
- Mas o `main.py` NÃO configura o FastAPI para servir arquivos estáticos
- O frontend NÃO está acessível

---

## Serviços que Iniciaram
- ✅ db-orders (PostgreSQL) - OK
- ✅ db-users (PostgreSQL) - OK  
- ✅ db-products (PostgreSQL) - OK

## Serviços que Falharam
- ❌ orders - ImportError (circular import)
- ❌ users - ImportError (circular import)
- ❌ products - ImportError (circular import)

---

## Command usado para testar:
```bash
cd c:/Users/kauan/Desktop/integrador/ifoodclone7
docker-compose up --build
```

---

## Nota
Este arquivo documenta apenas os erros encontrados, sem tentar refatorar ou corrigir o código, conforme solicitado.

