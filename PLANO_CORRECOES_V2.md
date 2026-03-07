# Plano de Correções V2 - Sistema de Agentes

## Problemas e Soluções

### 1. FIX AGENT - Criar vs Editar
**Problema**: Fix Agent cria novos arquivos ao invés de editar existentes
**Solução**: Modificar lógica para:
- PRIMEIRO: Buscar arquivo existente em múltiplos caminhos
- SEGUNDO: Se existir, editar/ fazer patch
- TERCEIRO: Só criar novo se NÃO existir

### 2. FRONTEND AGENT
**Problema**: Frontend estático, não dinâmico
**Solução**: Novo agente no FINAL do fluxo:
- Lê rotas REST do backend gerado
- Gera frontend (React/Vue) que consome essas rotas
- Valida se funciona
- Corrige erros

### 3. VALIDAÇÃO DE EXECUÇÃO
**Problema**: Agentes não tentam rodar o código
**Solução**: Sistema de validação real:
- Tentar importar módulos Python
- Verificar syntax errors
- Testar se APIs sobem (sem banco)
- Aplicar correções determinísticas automáticas
- Só chamar LLM para erros complexos

---

## Implementação

### 1. Fix Agent - Editar Primeiro

```python
# agents/fix_agent.py - nova lógica
async def _apply_fixes(...):
    # NOVA LÓGICA: Editar primeiro, criar depois
    
    for fix in fixes:
        file_path = fix.get("file_path")
        
        # 1. Tentar encontrar arquivo existente em MÚLTIPLOS caminhos
        existing_path = self._find_existing_file(file_path, project_path)
        
        if existing_path:
            # 2. ARQUIVO EXISTE → EDITAR
            existing_content = file_manager.read_file(existing_path)
            patched = self._apply_patch(existing_content, fix)
            file_manager.create_file(existing_path, patched)
            files_modified.append(existing_path)
        else:
            # 3. NÃO EXISTE → CRIAR (só agora!)
            file_manager.create_file(file_path, content)
            files_created.append(file_path)
```

### 2. Frontend Agent - Novo Agente

```python
# agents/frontend_agent.py
class FrontendAgent:
    """
    Agente para gerar frontend dinâmico após backend estar pronto.
    
    Fluxo:
    1. Lê rotas REST do backend
    2. Gera projeto React/Vue completo
    3. Cria componentes que consomem as APIs
    4. Valida se funciona
    5. Corrige erros se necessário
    """
    
    async def execute(self, backend_project_path):
        # 1. Extrair rotas do backend
        routes = self._extract_routes_from_backend(backend_project_path)
        
        # 2. Gerar frontend React
        frontend_files = self._generate_react_app(routes)
        
        # 3. Criar componentes dinamicos
        components = self._generate_crud_components(routes)
        
        # 4. Validar (tentar buildar)
        build_result = await self._validate_build(frontend_files)
        
        # 5. Se falhar, corrigir
        if not build_result.success:
            fixed = await self._fix_build_errors(build_result.errors)
            
        return frontend_files
```

### 3. Validação de Execução

```python
# infrastructure/runtime_validator.py
class RuntimeValidator:
    """
    Valida se o código realmente executa, não apenas estrutura.
    """
    
    async def validate_execution(self, project_path):
        results = {}
        
        # Para cada serviço
        for service in services:
            # 1. Testar imports
            import_result = self._test_imports(service)
            
            # 2. Testar syntax
            syntax_result = self._test_syntax(service)
            
            # 3. Testar se app FastAPI sobe (sem banco)
            startup_result = await self._test_startup(service)
            
            results[service] = {
                "imports": import_result,
                "syntax": syntax_result,
                "startup": startup_result
            }
        
        return results
    
    def _test_imports(self, service_path):
        """Tentar importar o módulo principal."""
        try:
            # Adicionar ao path
            sys.path.insert(0, service_path)
            import main  # Tenta importar
            return {"success": True}
        except ImportError as e:
            return {"success": False, "error": str(e)}
        except SyntaxError as e:
            return {"success": False, "syntax_error": str(e)}
    
    async def _test_startup(self, service_path):
        """Tentar iniciar o FastAPI (sem banco)."""
        try:
            from fastapi.testclient import TestClient
            # Importar app
            sys.path.insert(0, service_path)
            from main import app
            
            client = TestClient(app)
            response = client.get("/health")
            
            return {"success": True, "status": response.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 4. Corretor de Erros Comuns

```python
# agents/common_error_fixer.py
class CommonErrorFixer:
    """
    Corrige erros comuns automaticamente, sem precisar de LLM.
    """
    
    COMMON_FIXES = {
        "No module named 'email-validator'": {
            "action": "add_dependency",
            "dependency": "email-validator>=2.0.0"
        },
        "cannot import name 'Request'": {
            "action": "add_import",
            "import": "from fastapi import Request"
        },
        "Missing column": {
            "action": "fix_migration"
        }
    }
    
    def detect_and_fix(self, error_message, file_path):
        for pattern, fix in self.COMMON_FIXES.items():
            if pattern in error_message:
                return self._apply_fix(fix, file_path)
        
        # Se não é erro comum, retorna None para usar LLM
        return None
```

---

## Fluxo Revisado do Orchestrator

```
REQUISITOS
    │
    ▼
┌─────────────────┐
│  EXECUTOR      │ ◄── Gera código
│  AGENT         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VALIDATOR     │ ◄── Valida estrutura
│  AGENT         │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
APROVADO  REPROVADO
    │         │
    ▼         ▼
┌────────┐  ┌─────────────────┐
│FIX     │  │  FIX AGENT      │
│AGENT   │  │  (editar antes) │
└───┬────┘  └────────┬────────┘
    │                │
    └───────┬────────┘
            ▼
    ┌─────────────────┐
    │ RUNTIME         │ ◄── NOVO: Tenta rodar!
    │ VALIDATOR       │
    └────────┬────────┘
            │
     ┌──────┴──────┐
     ▼             ▼
  SUCESSO      FALHA
     │             │
     ▼             ▼
┌─────────┐  CORRIGIR AUTOMÁTICO
│BACKEND  │  (erros comuns) ou
│PRONTO   │  LLM (erros complexos)
└────┬────┘
     │
     ▼
┌─────────────────┐
│ FRONTEND       │ ◄── NOVO: Gera frontend
│ AGENT          │     que consome APIs
└────────┬────────┘
         │
         ▼
    ┌──────────┐
    │VALIDAR   │
    │FRONTEND  │
    └────┬─────┘
         │
    ┌────┴────┐
    ▼         ▼
 SUCESSO   CORRIGIR
    │
    ▼
✅ SISTEMA COMPLETO
```

---

## Próximos Passos

1. Modificar Fix Agent para editar primeiro
2. Criar RuntimeValidator
3. Criar FrontendAgent
4. Atualizar Orchestrator com novo fluxo

Quer que eu implemente isso? Por onde começar?
