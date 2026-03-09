# Plano para Testar e Corrigir o Sistema de Geração de Código

## 📊 Resumo da Execução Atual

O sistema foi executado para gerar um clone do iFood com microserviços para:
- Pedidos
- Clientes  
- Entregadores
- Pagamentos

**Resultado:** ❌ FALHA - 3 tentativas de auto-reparo esgotadas

---

## 🔴 Problemas Identificados

### 1. **Geração de Código Inicial com Defeitos** (RAIZ DO PROBLEMA)

O CodeAgent gerou arquivos com erros fundamentais:

#### 1.1 Arquivos `__init__.py` Inválidos
- `services/clientes/api/__init__.py` contém apenas: `"API Layer"`
- `services/clientes/application/__init__.py` contém apenas: `"Application Layer - clientes"`
- **Resultado:** Syntax Error - não é Python válido

#### 1.2 Imports Errados nos Arquivos `main.py`
```python
# ERRADO - main.py tenta importar de 'api.routes'
from api.routes import router

# O arquivo api/routes.py não existe ou não exports o router
```

#### 1.3 Arquivos Ausentes
- `api/routes.py` não foi criado pelo CodeAgent
- Arquivos de domínio com código incompleto

---

### 2. **Falha do Self-Repair Loop**

#### 2.1 Problema de Contexto
O CodeAgent recebe erros de runtime para correção, mas:
- Os erros não incluem informação suficiente sobre QUAL arquivo corrigir
- O contexto fornecido é muito grande (76 arquivos) e o LLM se perde

#### 2.2 Placeholder Detection Disparado Demais
O método `_looks_like_placeholder()` está sendo muito agressivo:
```python
markers = ["todo", "placeholder", "add your code", "implement here"]
```
Qualquer arquivo com estas palavras é ignorado, mesmo quando tem código real.

#### 2.3 Limite de 3 Tentativas Insuficiente
Com 22 erros e apenas 3 tentativas, não há tempo suficiente para correção.

---

### 3. **Bug no FrontendAgent** (Erro Fatal)

```
AttributeError: type object 'AgentType' has no attribute 'EXECUTOR'
```

O arquivo `frontend_agent.py` usa `AgentType.EXECUTOR`, mas o enum só tem:
```python
class AgentType(Enum):
    CODE = "code"
    RUNTIME_RUNNER = "runtime_runner"
    ROLLBACK = "rollback"
    ORCHESTRATOR = "orchestrator"
    FRONTEND = "frontend"
```

---

## 🛠️ Correções Necessárias

### Correção 1: Corrigir o FrontendAgent (CRÍTICO - Bloqueia Execução)

**Arquivo:** `agents/frontend_agent.py`

```python
# MUDAR de:
agent_type=AgentType.EXECUTOR,

# PARA:
agent_type=AgentType.CODE,
```

---

### Correção 2: Melhorar a Geração de __init__.py

**Arquivo:** `agents/code_agent.py`

Adicionar método para gerar `__init__.py` válidos:

```python
def _generate_init_file(self, layer: str, service_name: str = "") -> str:
    """Gera arquivo __init__.py válido."""
    if layer == "api":
        return '"""API Layer."""\nfrom .routes import router\n'
    elif layer == "application":
        return f'"""Application Layer - {service_name}."""\n'
    elif layer == "infrastructure":
        return '"""Infrastructure Layer."""\n'
    elif layer == "domain":
        return f'"""Domain Layer - {service_name}."""\n'
    return '"""\n'
```

---

### Correção 3: Corrigir Imports nos Arquivos main.py

O prompt de geração deve especificar que `main.py` deve usar imports relativos:

```python
# CORRETO - imports relativos
from .api.routes import router

# OU - imports absolutos com base no serviço
from services.clientes.api.routes import router
```

---

### Correção 4: Melhorar o Self-Repair Loop

**Arquivo:** `agents/code_agent.py`

1. Aumentar tentativas de reparo:
```python
max_repair_attempts: int = 5  # Mudar de 3 para 9
```

2. Melhorar o prompt de correção para ser mais específico:
```
CORRIJA ESTES ARQUIVOS ESPECÍFICOS (não gere novos):
1. services/clientes/api/__init__.py - Syntax Error
2. services/clientes/main.py - Import Error (api.routes)
```

3. Reduzir contexto enviado ao LLM:
- Enviar apenas os arquivos com erro, não todos os 76
-enviar uma list do contexto do restante do projeto


---

### Correção 5: Adicionar Validação Prévia no CodeAgent

Antes de retornar sucesso, verificar se os arquivos básicos existem:

```python
def _validate_basic_structure(self, file_manager, service_name) -> bool:
    """Valida estrutura básica do serviço."""
    required_files = [
        f"services/{service_name}/domain/__init__.py",
        f"services/{service_name}/api/routes.py",
        f"services/{service_name}/main.py",
    ]
    for f in required_files:
        if not file_manager.file_exists(f):
            return False
    return True
```

---

## 📋 Passos para Testar o Sistema Corrigido

### Passo 1: Aplicar Correções
1. Corrigir `frontend_agent.py` (linha 46)
2. Corrigir geração de `__init__.py` em `code_agent.py`
3. Corrigir prompts para imports corretos
4. Aumentar tentativas de repair loop

### Passo 2: Limpar Projeto Gerado
```bash
# Remover projeto com falha
rm -rf ifoodclone
```

### Passo 3: Reiniciar API
```bash
# Reiniciar o servidor
python -m uvicorn api.server:app --reload --port 8000
```

### Passo 4: Nova Requisição
```json
{
  "requirements": "Criar um clone do iFood com microserviços para gerenciamento de pedidos, clientes, entregadores e pagamentos",
  "model": "llama3.2",
  "output": "ifoodclone",
  "framework": "python-fastapi",
  "database": "postgresql"
}
```

---

## 🎯 Métricas de Sucesso Esperadas

| Métrica | Target |
|---------|--------|
| Arquivos gerados | 60+ |
| Services válidos | 4/4 |
| Self-repair attempts | ≤3 |
| Tempo total | < 5 min |
| Resultado final | ✅ SUCCESS |

---

## 📝 Anotações Adicionais

### O que está funcionando bem:
1. ✅ API FastAPI respondendo
2. ✅ Ollama conectado e gerando código
3. ✅ Estrutura de microservices identificada corretamente
4. ✅ WebSocket atualizando frontend
5. ✅ 78 arquivos criados na primeira geração

### O que precisa melhorar:
1. ❌ Qualidade do código gerado (syntax errors em __init__.py)
2. ❌ Self-repair loop (não consegue corrigir os erros)
3. ❌ Validação de estrutura antes de retornar sucesso

---

## 🚀 Recomendação de Ação Imediata

Para teste rápido, as correções mais importantes são:

1. **CRÍTICO:** Corrigir `AgentType.EXECUTOR` → `AgentType.CODE` no frontend_agent.py
2. **Alta prioridade:** Melhorar geração de `__init__.py` 
3. **Média prioridade:** Aumentar tentativas de repair loop

Com apenas a correção #1, o sistema deve pelo menos avanzar para geração do frontend após falhar no backend.

