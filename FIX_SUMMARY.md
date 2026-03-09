# Resumo das Correções Necesárias para o Sistema de Agentes

## ✅ Correção Já Aplicada

### 1. FrontendAgent - AgentType.EXECUTOR
**Arquivo:** `agents/frontend_agent.py`
**Linha:** ~46
**Mudança:**
```python
# De:
agent_type=AgentType.EXECUTOR,

# Para:
agent_type=AgentType.CODE,
```
**Status:** ✅ CORRIGIDO

---

## 🔴 Correções Pendentes - Geracao de Codigo

### 2. Arquivos __init__.py Inválidos

**Arquivo:** `agents/code_agent.py`
**Método:** `_generate_ddd_structure()`

O código atual gera arquivos inválidos para `__init__.py`:

```python
# ATUAL (ERRADO):
files[f"{base_path}/application/__init__.py"] = f"Application Layer - {service_name}\n"
files[f"{base_path}/infrastructure/__init__.py"] = "Infrastructure Layer\n"
files[f"{base_path}/api/__init__.py"] = "API Layer\n"
```

**CORREÇÃO NECESSÁRIA - Substituir por:**

```python
# Application Layer
files[f"{base_path}/application/__init__.py"] = f'''"""Application Layer - {service_name}."""
from .dtos import *
from .mappers import *
from .use_cases import *
'''

# Infrastructure Layer
files[f"{base_path}/infrastructure/__init__.py"] = '''"""Infrastructure Layer."""
from .repositories import *
from .database import *
'''

# API Layer
files[f"{base_path}/api/__init__.py"] = '''"""API Layer."""
from .routes import router
from .schemas import *
'''
```

---

### 3. Imports nos Arquivos main.py

**Arquivo:** `agents/code_agent.py`
**Método:** `_generate_main()`

O código atual gera:
```python
from api.routes import router  # ERRADO - não funciona
```

**CORREÇÃO NECESSÁRIA:**
```python
def _generate_main(self, service_name: str) -> str:
    """Generate main.py."""
    return f'''"""Main application for {service_name}."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import correto - usa import relativo
from .api.routes import router

app = FastAPI(title="{service_name}", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
```

---

## 🔴 Correções Pendentes - Self-Repair Loop

### 4. Placeholder Detection Muito Agressiva

**Arquivo:** `agents/code_agent.py`
**Método:** `_looks_like_placeholder()`

**Problema:** O método atual marca como placeholder qualquer arquivo que contenha palavras como "email", "datetime", etc.

**CORREÇÃO NECESSÁRIA:**
```python
def _looks_like_placeholder(self, content: str) -> bool:
    """Check if content is a placeholder."""
    if not content:
        return True
    
    # Reduzir falsos positivos - só marca como placeholder se for muito curto ou só tiver marcações claras
    content_lower = content.lower().strip()
    
    # Só marca como placeholder se for muito curto ou só tiver texto genérico
    if len(content) < 50:
        return True
    
    # Marcadores claros de placeholder (não marcar arquivos reais)
    clear_markers = ["todo:", "placeholder:", "add your code here", "implement this"]
    
    return any(marker in content_lower for marker in clear_markers)
```

---

### 5. Aumentar Tentativas de Repair

**Arquivo:** `agents/orchestrator_v3.py`

**CORREÇÃO NECESSÁRIA:**
```python
# Na inicialização do OrchestratorV3
self.max_repair_attempts = 5  # Mudar de 3 para 5
```

---

### 6. Melhorar Contexto do Self-Repair

**Arquivo:** `agents/code_agent.py`
**Método:** `_build_full_project_context()`

O contexto atual envia 76 arquivos, sobrecarregando o LLM.

**CORREÇÃO:** Reduzir para apenas os arquivos com erro:
```python
def _build_context_for_errors(self, errors: list[dict], file_manager, all_files) -> str:
    """Build context only for files with errors."""
    # Extrai nomes de arquivos com erro
    error_files = set()
    for error in errors:
        # Tenta identificar o arquivo pelo erro
        msg = error.get("message", "")
        # Adicionar lógica para identificar arquivo
        
    # Carrega apenas esses arquivos
    snippets = []
    for f in all_files:
        if any(ef in f for ef in error_files):
            content = file_manager.read_file(f)
            if content:
                snippets.append(f"### {f}\n```python\n{content[:1500]}\n```")
    
    return "\n\n".join(snippets)
```

---

## 📋 Resumo de Arquivos para Testar

Para testar o sistema corrigido:

1. Aplique as correções pendentes acima
2. Delete a pasta `ifoodclone` (se existir)
3. Reinicie a API
4. Envie nova requisição

---

## 🎯 Prioridades de Correção

| Prioridade | Correção | Impacto |
|------------|----------|---------|
| **ALTA** | __init__.py válidos | Resolve syntax errors |
| **ALTA** | Imports main.py | Resolve import errors |
| **MEDIA** | Placeholder detection | Permite repairs funcionarem |
| **MEDIA** | Aumentar attempts | Mais chances de sucesso |
| **BAIXA** | Contexto otimizado | Performance |

