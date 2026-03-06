# Erros Identificados no ifoodclone12

## Visão Geral
Ao tentar rodar o ifoodclone12 via Docker, os serviços **orders** e **users** apresentam erros e não iniciam corretamente.

---

## 1. Orders Service - ERRO

### Sintoma
```
ImportError: cannot import name 'Order' from 'domain.orders_entities'
```

### Causa Raiz
O arquivo `domain/__init__.py` tenta importar:
```python
from .orders_entities import Order, OrderRepository
```

Mas o arquivo `orders_entities.py` contém classes erradas:
- `Product` (deveria ser `Order`)
- `ProductRepository` (deveria ser `OrderRepository`)

### Arquivo Afetado
- `ifoodclone12/services/orders/domain/orders_entities.py`

### Correção Necessária
Renomear as classes de `Product` → `Order` e `ProductRepository` → `OrderRepository`

---

## 2. Users Service - ERRO

### Sintoma
```
ModuleNotFoundError: No module named 'email_validator'
ImportError: email-validator is not installed, run `pip install 'pydantic[email]'`
```

### Causa Raiz
O arquivo `requirements.txt` não inclui a dependência `email-validator`, que é necessária quando se usa `EmailStr` do Pydantic.

### Arquivo Afetado
- `ifoodclone12/services/users/requirements.txt`

### Correção Necessária
Adicionar ao requirements.txt:
```
email-validator>=2.0.0
```

---

## 3. Products Service - OK

O serviço de products está funcionando corretamente:
- Container rodando na porta 32783
- Respondendo em `/health`

---

## 4. Payment Service - OK

O serviço de payment está funcionando corretamente:
- Container rodando na porta 32784
- Respondendo em `/health`

---

## Logs de Referência

### Orders
```
Traceback (most recent call last):
  File "/app/main.py", line 9, in <module>
    from api.routes import router
  File "/app/api/routes.py", line 12, in <module>
    from application.use_cases import (
  File "/app/application/use_cases.py", line 8, in <module>
    from domain.orders_entities import Order
  File "/app/domain/__init__.py", line 2, in <module>
    from .orders_entities import Order, OrderRepository
ImportError: cannot import name 'Order' from 'domain.orders_entities'
```

### Users
```
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/pydantic/networks.py", line 965, in import_email_validator
    import email_validator
ModuleNotFoundError: No module named 'email_validator'
...
ImportError: email-validator is not installed, run `pip install 'pydantic[email]'`
```

---

## Containers Atuais (docker ps -a)

| Container | Status | Porta |
|-----------|--------|-------|
| ifoodclone12-orders-1 | Exited (1) | - |
| ifoodclone12-users-1 | Exited (1) | - |
| ifoodclone12-products-1 | Up | 32783 |
| ifoodclone12-payment-1 | Up | 32784 |
| ifoodclone12-db-orders-1 | Up | 5432 |
| ifoodclone12-db-users-1 | Up | 5432 |
| ifoodclone12-db-products-1 | Up | 5432 |
| ifoodclone12-db-payment-1 | Up | 5432 |

