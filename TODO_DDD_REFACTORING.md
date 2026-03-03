# TODO - Refatoração DDD do Sistema de Agentes

## Fase 1: Atualização do Modelo de Entidades ✅ COMPLETO
- [x] 1.1 Adicionar `BoundedContextSpec` em `domain/entities.py`
- [x] 1.2 Adicionar `AggregateSpec` em `domain/entities.py`
- [x] 1.3 Adicionar `ValueObjectSpec` em `domain/entities.py`
- [x] 1.4 Adicionar `DomainEventSpec` em `domain/entities.py`
- [x] 1.5 Atualizar `Requirement` para aceitar estrutura DDD

## Fase 2: Novos Prompts DDD ✅ COMPLETO
- [x] 2.1 Criar `build_ddd_executor_prompt` em `llm_provider.py`
- [x] 2.2 Atualizar `build_executor_prompt` para detectar modo DDD
- [x] 2.3 Adicionar sistema de detecção de anemia de domínio (no validator)

## Fase 3: Templates de Geração DDD 📋 PARCIAL (via LLM)
- [x] 3.0 Prompts DDD agora instruem o LLM a gerar código correto

## Fase 4: Separação Rigorosa de Camadas 📋 PARCIAL
- [x] 4.0 Prompts DDD instruem sobre separação correta

## Fase 5: Validação de Anemia ✅ COMPLETO
- [x] 5.1 Adicionar detector de entidades sem comportamento
- [x] 5.2 Adicionar detector de regras em controllers
- [x] 5.3 Adicionar verificador de dependências reversas

## Fase 6: Testes de Domínio 📋 PENDENTE
- [ ] 6.1 Gerar testes de Aggregate Root
- [ ] 6.2 Gerar testes de Use Cases (com mocks)
- [ ] 6.3 Gerar testes de Value Objects

## Fase 7: Exemplo de Bounded Context Gerado ✅ COMPLETO
- [x] 7.1 Gerar exemplo completo de "Billing" context
- [x] 7.2 Documentar as regras DDD aplicadas

---

## Progresso Total: ~70% Completo

### O que foi feito:
1. ✅ Novo modelo de entidades com suporte a Bounded Contexts, Aggregates, Value Objects, Domain Events
2. ✅ Prompts DDD Estratégicos no PromptBuilder com regras rigorosas
3. ✅ Sistema de validação de anemia de domínio
4. ✅ Sistema de verificação de pureza da camada de domínio
5. ✅ Verificação de separação de interfaces de repositório
6. ✅ Exemplo completo de Bounded Context "Billing" com:
   - Invoice Entity com comportamento
   - Money Value Object com validações
   - InvoiceAggregate com invariantes
   - Domain Events
   - Repository Interface no domínio
   - Repository Implementation na infraestrutura
   - Use Cases de aplicação

### Como usar o novo sistema DDD:

```python
from domain.entities import (
    Requirement, 
    ProjectConfig, 
    BoundedContextSpec,
    EntitySpec,
    ValueObjectSpec,
    UseCaseSpec
)

# Criar especificação DDD
billing_context = BoundedContextSpec(
    name="Billing",
    aggregate_root="Invoice",
    entities=[
        EntitySpec(name="Invoice", attributes={"customer_id": "UUID"}, behaviors=["add_item", "close", "pay"]),
        EntitySpec(name="InvoiceItem", attributes={"description": "str", "quantity": "int"})
    ],
    value_objects=[
        ValueObjectSpec(name="Money", attributes={"amount": "Decimal", "currency": "str"})
    ],
    use_cases=[
        UseCaseSpec(name="CreateInvoice", steps=["validate", "create_aggregate", "save"]),
        UseCaseSpec(name="AddItemToInvoice", steps=["get_aggregate", "add_item", "save"]),
        UseCaseSpec(name="CloseInvoice", steps=["get_aggregate", "validate", "close"])
    ]
)

# Criar requirement com modo DDD
requirement = Requirement(
    description="Sistema de billing com faturas",
    project_config=ProjectConfig(output_directory="generated"),
    bounded_contexts=[billing_context],
    use_ddd_mode=True  # Ativa modo DDD
)
```

