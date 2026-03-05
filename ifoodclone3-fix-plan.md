# Plano de Correção Rápida — ifoodclone3

Este guia transforma os problemas documentados em `tryingtorunifood3.md` em ações práticas, com alterações mínimas para o projeto subir via Docker Compose.

## 1) Corrigir erro de import nos serviços Python

### Opção recomendada (mais simples): usar import absoluto

Em cada serviço (`orders`, `users`, `products`), no arquivo `main.py`, troque:

```python
from .api.routes import router
```

por:

```python
from api.routes import router
```

Com isso, o comando atual do Dockerfile (`python main.py`) passa a funcionar sem depender de execução como pacote.

---

### Opção alternativa: manter import relativo e mudar execução

Se quiser manter `from .api.routes import router`, faça os dois passos abaixo:

1. Garanta que exista `__init__.py` em todos os diretórios de pacote relevantes.
2. No Dockerfile, substitua:

```dockerfile
CMD ["python", "main.py"]
```

por algo no formato:

```dockerfile
CMD ["python", "-m", "services.orders.main"]
```

> Observação: essa abordagem exige que a estrutura de diretórios dentro do container reflita o path de módulo usado no `-m`.

## 2) Fixar versão do PostgreSQL para evitar incompatibilidade de volume

No `docker-compose.yml`, para os bancos (`db-orders`, `db-users`, `db-products`), troque:

```yaml
image: postgres
```

por:

```yaml
image: postgres:16
```

Isso evita mudanças inesperadas da tag `latest` (que pode apontar para 18+).

## 3) Limpar volumes antigos incompatíveis

> **Atenção:** os comandos abaixo removem dados locais dos bancos.

```bash
docker compose down
docker volume rm ifoodclone3_pgdata-orders ifoodclone3_pgdata-users ifoodclone3_pgdata-products
```

Se os nomes exatos dos volumes forem diferentes, descubra com:

```bash
docker volume ls | grep ifoodclone3
```

## 4) Subir novamente e validar

```bash
docker compose up --build -d
docker compose ps
docker compose logs orders users products --tail=100
```

Valide que não há mais:
- `ImportError: attempted relative import with no known parent package`
- erro de inicialização do PostgreSQL por formato de diretório de versão

## 5) Checklist de aceite

- [ ] `orders` sobe sem `ImportError`
- [ ] `users` sobe sem `ImportError`
- [ ] `products` sobe sem `ImportError`
- [ ] bancos `db-orders`, `db-users`, `db-products` ficam `healthy`/`running`
- [ ] endpoints de healthcheck respondem HTTP 200

---

## Estratégia de prevenção (curto prazo)

- Sempre fixar tags de imagem (`postgres:16`, `python:3.11-slim`, etc.).
- Evitar `latest` em ambientes de desenvolvimento reproduzível.
- Definir padrão de imports por projeto (absoluto com `python main.py` **ou** relativo com `python -m ...`).
- Adicionar validação CI para subir stack mínima com `docker compose up`.
