# Plano de Correção: Self-Repair Loop com Parse JSON

## Problema Identificado

O loop de self-repair está falhando porque:
1. O parser `_parse_fix_json` no CodeAgent espera JSON estruturado
2. O modelo (Qwen Coder) responde com texto/markdown ao invés de JSON
3. O parser falha e nenhum arquivo é modificado
4. Loop infinito de validação sem correção

## Causa Raiz

O método `_parse_fix_json` no `CodeAgent` é muito simples:

```python
def _parse_fix_json(self, llm_output: str) -> dict:
    try:
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None
```

Este parser falha quando:
- O modelo retorna markdown com JSON em blocos de código
- O modelo retorna texto explicativo ao invés de JSON
- O JSON está incompleto ou malformado

## Soluções a Implementar

### 1. Melhorar o Prompt de Fix (code_agent.py)

Modificar `_build_fix_prompt` para FORÇAR saída JSON válida:

```python
# NOVO PROMPT - Mais explícito sobre formato JSON
"""
IMPORTANT - RESPONSE FORMAT:
You MUST respond ONLY with valid JSON. No explanations, no markdown, no code blocks.

JSON Structure:
{
  "fixes": [
    {
      "file_path": "path/to/file.py",
      "action": "modify",
      "content": "FULL FILE CONTENT HERE"
    }
  ]
}

Do NOT include:
- Any text before or after the JSON
- Markdown code blocks (```)
- Explanations or comments
- Partial file contents - always include complete file for "modify" action
"""
```

### 2. Melhorar o Parser de JSON (code_agent.py)

Modificar `_parse_fix_json` para ser mais robusto:

```python
def _parse_fix_json(self, llm_output: str) -> dict:
    """
    Parse JSON from LLM output with multiple fallback strategies.
    """
    # Strategy 1: Extract from markdown code blocks
    if "```" in llm_output:
        blocks = llm_output.split("```")
        for block in blocks[1:]:  # Skip text before first ```
            # Skip language specifier (e.g., ```json)
            content = block.strip()
            if content.startswith("json"):
                content = content[4:].strip()
            elif content.startswith("python"):
                content = content[6:].strip()
            
            try:
                return json.loads(content)
            except:
                continue
    
    # Strategy 2: Find first { and last } to extract JSON
    json_start = llm_output.find('{')
    if json_start >= 0:
        # Find matching closing brace
        depth = 0
        for i, char in enumerate(llm_output[json_start:]):
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(llm_output[json_start:json_start+i+1])
                    except:
                        pass
                    break
    
    # Strategy 3: Clean common issues and retry
    cleaned = llm_output.strip()
    cleaned = re.sub(r'^```json\s*', '', cleaned)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'```$', '', cleaned)
    cleaned = re.sub(r',\s*}', '}', cleaned)  # trailing commas
    cleaned = re.sub(r',\s*]', ']', cleaned)
    
    try:
        return json.loads(cleaned)
    except:
        pass
    
    return None
```

### 3. Reduzir Contexto Enviado ao Modelo

Modificar `_build_full_project_context` para enviar apenas arquivos relevantes:

```python
def _build_targeted_context(
    self,
    file_manager: FileManager,
    runtime_errors: list[dict]
) -> str:
    """
    Build MINIMAL context - only files with errors and their dependencies.
    """
    # Extract file paths from errors
    error_files = set()
    for error in runtime_errors:
        if "file" in error:
            error_files.add(error["file"])
    
    # For each error file, also include files in the same directory
    # and any imports
    context_files = []
    
    for error_file in error_files:
        # Add the error file itself
        if file_manager.file_exists(error_file):
            content = file_manager.read_file(error_file)
            context_files.append(f"### {error_file}\n```python\n{content[:2000]}\n```")
        
        # Find related files in same service
        service_dir = str(Path(error_file).parent)
        related = file_manager.list_files(service_dir)
        
        # Add key files from same service
        priority = ["main.py", "requirements.txt", "__init__.py"]
        for f in related:
            if any(p in f for p in priority) and f not in error_files:
                content = file_manager.read_file(f)
                if content:
                    context_files.append(f"### {f}\n```python\n{content[:1000]}\n```")
    
    return "\n\n".join(context_files)
```

### 4. Adicionar Fallback para Text Response

Se o parsing falhar, tentar extrair informações de texto:

```python
def _try_extract_fixes_from_text(self, llm_output: str, file_manager: FileManager) -> list:
    """
    Fallback: Try to extract file paths and apply simple fixes from text.
    """
    fixes = []
    
    # Look for file paths in the response
    file_pattern = r'(?:file|path|arquivo)[:\s]+([a-zA-Z0-9_/\\.-]+\.py)'
    matches = re.finditer(file_pattern, llm_output, re.IGNORECASE)
    
    for match in matches:
        file_path = match.group(1)
        if file_manager.file_exists(file_path):
            fixes.append({
                "file_path": file_path,
                "action": "modify",
                "content": file_manager.read_file(file_path),  # Keep as-is for now
                "reason": "File mentioned in LLM response but JSON parse failed"
            })
    
    return fixes
```

## Arquivos a Modificar

1. **agents/code_agent.py**:
   - `_build_fix_prompt()` - Melhorar prompt
   - `_parse_fix_json()` - Parser mais robusto
   - `_build_full_project_context()` - Contexto mínimo
   - `_apply_fixes()` - Adicionar fallback

## Testes a Executar

1. Gerar novo projeto
2. Forçar erro de runtime (import faltando)
3. Verificar se o self-repair aplica correções
4. Verificar se erros de parsing aparecem nos logs

## Status: PENDENTE

As correções precisam ser implementadas e testadas.

