# Relatório Técnico: Diagnóstico do Sistema de Geração de Microserviços

## 1. RESUMO EXECUTIVO

O sistema atual gera microserviços com estrutura DDD básica, porém apresenta **problemas fundamentais de anemia de domínio** e violação de princípios de Clean Architecture. A refatoração é necessária para transformar o gerador em um verdadeiro sistema de modelagem de domínio estratégico e tático.

---

## 2. PROBLEMAS IDENTIFICADOS

### 2.1 Domínio Anêmico (CRUD Anêmico)

**Problema:** As entidades geradas são meros containers de dados sem regras de negócio.

**Evidência em `generated/services/academia/domain/usuario.py`:**
```python
@dataclass
class Usuario:
    id: UUID
    nome: str
    email: str
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(nome: str, email: str, **kwargs) -> "Usuario":
        # Apenas cria o objeto sem validação
        return Usuario(...)
    
    def update(self, **kwargs):
        # Apenas setta atributos sem regras
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
```

**Impacto:** Regras de negócio estão dispersas nos controllers ou use cases.

---

### 2.2 Mistura de Camadas (Layer Violation)

**Problema:** O domínio depende de frameworks de infraestrutura.

**Evidência em `generated/services/academia/domain/academia_entities.py`:**
```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # FRAMEWORK NO DOMÍNIO!

class UsuarioEntity(Base):  # ORM NO DOMÍNIO!
    __tablename__ = "usuarios"
    ...
```

**Violação:** O domínio NUNCA deve importar frameworks. O `Base` do SQLAlchemy está no domain layer.

---

### 2.3 Falta de Aggregate Root

**Problema:** Não há conceito de agregação com raiz de agregado.

**O que existe:**
- Entidades soltas (`Usuario`, `Treino`)
- Sem controle de invariantes
- Sem encapsulamento de entidades filhas

**O que deveria existir:**
```python
class InvoiceAggregate:
    """Aggregate Root - controla invariantes"""
    def __init__(self):
        self._root: Invoice = None
        self._items: list[InvoiceItem] = []
    
    def add_item(self, item: InvoiceItem):
        # Regra: não permite item com valor negativo
        if item.amount < 0:
            raise DomainException("Item não pode ter valor negativo")
        self._items.append(item)
```

---

### 2.4 Falta de Value Objects Ricos

**Problema:** Value Objects gerados são apenas dataclasses sem validação.

**O que existe:**
```python
@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "BRL"
```

**O que deveria existir:**
```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "BRL"
    
    def __post_init__(self):
        if self.amount < 0:
            raise DomainException("Valor não pode ser negativo")
    
    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise DomainException("Moedas diferentes")
        return Money(self.amount + other.amount, self.currency)
```

---

### 2.5 Falta de Domain Events

**Problema:** Nenhum evento de domínio é gerado ou utilizado.

**O que deveria existir:**
```python
@dataclass
class DomainEvent:
    event_id: UUID
    occurred_on: datetime
    event_type: str

@dataclass
class InvoiceClosedEvent(DomainEvent):
    invoice_id: UUID
    total_amount: Money
```

---

### 2.6 Repository Implementado no Domínio

**Problema:** Interfaces de repositório estão no domínio (correto), mas implementações violam a arquitetura.

**Evidência em `generated/services/academia/infrastructure/repositories.py`:**
- Boa parte da implementação está correta (separation of concerns)
- MAS: O domain importa a implementação em alguns casos

---

### 2.7 Input Não-Estruturado

**Problema:** O sistema aceita apenas descrição textual, sem modelo de domínio estruturado.

**O que existe:**
```python
requirement.description = "Crie um sistema de academia com usuários"
```

**O que deveria existir:**
```python
requirement.bounded_context = "Billing"
requirement.aggregate_root = "Invoice"
requirement.entities = ["InvoiceItem"]
requirement.value_objects = ["Money"]
requirement.domain_services = ["PaymentProcessor"]
requirement.use_cases = ["CreateInvoice", "AddItemToInvoice", "CloseInvoice"]
```

---

### 2.8 Use Cases Sem Orchestração

**Problema:** Use cases são wrappers CRUD simples.

**Evidência em `generated/services/academia/application/use_cases.py`:**
```python
class CreateUsuarioUseCase:
    async def execute(self, data: dict) -> Usuario:
        entity = Usuario.create(**data)  # Apenas cria
        return await self.repository.save(entity)  # Apenas salva
```

**O que deveria existir:**
```python
class CreateInvoiceUseCase:
    async def execute(self, data: CreateInvoiceDTO) -> Invoice:
        # Validações de domínio
        customer = await self.customer_repository.get(data.customer_id)
        if not customer.is_active:
            raise DomainException("Cliente inativo")
        
        # Cria agregado com regras
        aggregate = InvoiceAggregate.create(customer)
        
        # Dispara eventos
        self.event_bus.publish(InvoiceCreatedEvent(...))
        
        # Salva
        return await self.invoice_repository.save(aggregate.root)
```

---

## 3. ANÁLISE COMPARATIVA

| Aspecto | Estado Atual | Estado Desejado (DDD) |
|---------|--------------|----------------------|
| Entidades | Data classes com getters/setters | Objetos com comportamento e regras |
| Value Objects | Dataclasses vazias | Objetos imutáveis com validação |
| Aggregates | Não existem | Raízes de agregado com invariantes |
| Domain Events | Não existem | Eventos para reações em cadeia |
| Repositories | Interface no domínio, implementação mista | Interface protocolo, implementação em infra |
| Use Cases | CRUD simples | Orchestração de agregados |
| Input | Texto livre | Modelo estruturado (bounded context) |
| Camadas | Misturadas | Rigorosamente separadas |

---

## 4. IMPACTO NOS AGENTES

### 4.1 Executor Agent
- **Necessita:** Modificação para aceitar input estruturado DDD
- **Necessita:** Novos templates de geração com regras de negócio
- **Necessita:** Gerar Aggregate Roots com validação
- **Necessita:** Gerar Domain Events
- **Necessita:** Gerar Value Objects com validação

### 4.2 Validator Agent
- **Necessita:** Nova validação para detectar anemia de domínio
- **Necessita:** Verificar se entidades têm comportamento
- **Necessita:** Verificar separação de camadas
- **Necessita:** Verificar dependências (domain não importa infra)

### 4.3 Fix Agent
- **Necessita:** Capacidade de corrigir código anêmico
- **Necessita:** Adicionar regras de negócio faltantes

### 4.4 PromptBuilder
- **Necessita:** Novos prompts DDD estratégicos
- **Necessita:** Prompts paramodelagem tática

---

## 5. RECOMENDAÇÕES DE REFATORAÇÃO

### Fase 1: Mudança no Modelo de Input
1. Criar nova classe `BoundedContextSpec` em `domain/entities.py`
2. Modificar `Requirement` para aceitar contexto delimitado estruturado
3. Atualizar `PromptBuilder` para usar o novo formato

### Fase 2: Novos Templates de Geração
1. Criar templates para Aggregate Root
2. Criar templates para Value Objects com validação
3. Criar templates para Domain Events
4. Criar templates para Domain Services
5. Criar templates para Application Services

### Fase 3: Separação Rigorosa de Camadas
1. Garantir que domain não importe sqlalchemy/orm
2. Mover entidades de banco para infrastructure/persistence
3. Criar mapeadores (domain <-> infrastructure)

### Fase 4: Validação de Anemia
1. Adicionar detector de entidades sem comportamento
2. Adicionar detector de regras em controllers
3. Adicionar verificador de dependências

### Fase 5: Testes de Domínio
1. Gerar testes unitários que não dependem de banco
2. Gerar testes de Use Cases com mocks
3. Gerar testes de Aggregate invariants

---

## 6. CONCLUSÃO

O sistema atual gera código com **estrutura DDD superficial** (arquivos organizados em pastas), mas **sem os conceitos fundamentais de DDD** (agregados, eventos de domínio, regras encapsuladas). A refatoração proposta transformará o gerador em uma ferramenta de **Domain-Driven Design real**, que produz código com modelagem de domínio rica e separação rigorosa de camadas.

A prioridade deve ser:
1. ✅ Input estruturado (Ubiquitous Language)
2. ✅ Entidades com comportamento (não anêmicas)
3. ✅ Aggregate Roots com invariantes
4. ✅ Value Objects com validação
5. ✅ Domain Events
6. ✅ Separação de camadas (Clean Architecture)
7. ✅ Testes de domínio

