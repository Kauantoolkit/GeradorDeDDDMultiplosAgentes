# ifoodclone10 - Erros Encontrados

Data da análise: Executei o docker-compose e verifiquei os logs de cada serviço.

---

## Status dos Serviços

| Serviço    | Status  | Porta |
|------------|---------|-------|
| orders     | ❌ ERRO | -     |
| users      | ❌ ERRO | -     |
| products   | ✅ OK   | 32771 |
| payment    | ✅ OK   | 32770 |
| reviews    | ✅ OK   | 32768 |

---

## Erro 1: Orders Service - ModuleNotFoundError

### Descrição
O serviço **orders** apresenta erro ao iniciar:

```
ModuleNotFoundError: No module named 'services'
```

### Causa Raiz
O arquivo `main.py` do serviço orders utiliza imports absolutos com o prefixo `services.orders.*`:

```python
# main.py - imports incorretos
from services.orders.application import OrderUseCase
from services.orders.infrastructure import OrderRepository
from services.orders.domain import Order
from services.orders.application import OrderService
from services.orders.domain import OrderStatus
```

No entanto, a estrutura de diretórios do projeto coloca os arquivos diretamente em:
- `application/`
- `domain/`
- `infrastructure/`

**Faltando o subdiretório `services/orders/`** para que os imports funcionem como estão.

### Solução Necessária
Os imports deveriam ser relativos ao diretório do serviço, por exemplo:
```python
from application import OrderUseCase
from infrastructure import OrderRepository
from domain import Order, OrderStatus
```

---

## Erro 2: Users Service - Dependência email-validator faltando

### Descrição
O serviço **users** apresenta erro ao iniciar:

```
ModuleNotFoundError: No module named 'email_validator'
ImportError: email-validator is not installed, run `pip install 'pydantic[email]'`
```

### Causa Raiz
O arquivo `api/schemas.py` utiliza `EmailStr` do pydantic:

```python
# api/schemas.py - linha 24
class CreateUserSchema(BaseModel):
    email: EmailStr  # <-- requer email-validator
```

Mas o arquivo `requirements.txt` do serviço **não inclui** a dependência `email-validator`:

```
# requirements.txt atual
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
python-dotenv>=1.0.0
```

### Solução Necessária
Adicionar ao requirements.txt:
```
email-validator>=2.0.0
```

---

## Serviços Funcionando Corretamente

### Products Service ✅
Iniciou sem erros. Logs mostram:
```
INFO: Started server process [1]
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Payment Service ✅
Iniciou sem erros. Logs mostram:
```
INFO: Started server process [1]
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Reviews Service ✅
Iniciou sem erros. Logs mostram:
```
INFO: Started server process [1]
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## Resumo dos Problemas

| # | Serviço | Problema | Tipo |
|---|---------|----------|------|
| 1 | orders | Imports incorretos (services.orders.*) | Código |
| 2 | users | Dependência email-validator faltando | Dependência |

---

## Observações

- O serviço orders possui uma pasta chamada `inrastructure/` (com erro de digitação - "inrastructure" em vez de "infrastructure") que também pode causar problemas
- O docker-compose.yml principal referencia os serviços sem Dockerfiles no diretório raiz (não tem Dockerfile em ./services/orders, ./services/users, etc), apenas os serviços que têm Dockerfiles próprios (orders, users, products, payment, reviews) são buildados

