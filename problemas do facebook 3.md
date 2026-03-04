# Problemas Encontrados no Clone Facebook 3

## Problema 1: Incompatibilidade de Nomes de Diretórios

**Descrição:**
O arquivo `docker-compose.yml` referencia os serviços usando nomes com hífen (ex: `order-service`, `product-service`, `user-service`, etc.), mas os diretórios físicos usam sublinhado (ex: `order_service`, `product_service`, `user_service`).

**Localização do erro:**
- docker-compose.yml linha com `context: ./services/order-service`
- docker-compose.yml linha com `context: ./services/product-service`
- docker-compose.yml linha com `context: ./services/user-service`
- docker-compose.yml linha com `context: ./services/auth-service`
- docker-compose.yml linha com `context: ./services/payment-service`

**Mensagem de erro:**
```
unable to prepare context: path "c:\Users\kauan\Desktop\integrador\clone facebook 3\services\order-service" not found
```

**Solução necessária (não implementada):**
O docker-compose.yml precisa ter os contexts ajustados para usar sublinhado em vez de hífen:
- `order-service` → `order_service`
- `product-service` → `product_service`
- `user-service` → `user_service`
- `auth-service` → `auth_service`
- `payment-service` → `payment_service`

Ou os diretórios precisam ser renomeados de sublinhado para hífen.

---

## Problema 2: Atributo 'version' Obsoleto

**Descrição:**
O docker-compose.yml usa o atributo `version` que está obsoleto nas versões recentes do Docker Compose.

**Mensagem de warning:**
```
the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
```

**Nota:** Este é apenas um warning e não impede a execução, mas indica que o arquivo está desatualizado.

