"""
Script de Debug para identificar erros comuns em f-strings
=========================================================

Este script verifica padrões problemáticos em f-strings que podem causar erros como:
- 'name 'k' is not defined' - comprehension dentro de f-string sem escape
- Problemas de escaping de chaves { }

Uso:
    python debug_fstring.py
"""

import os
import re
import ast
from pathlib import Path

# Padrões problemáticos a serem procurados
PROBLEMATIC_PATTERNS = [
    # comprehension dentro de f-string (sem escape)
    (r"f['\"].*\{[a-zA-Z_][a-zA-Z0-9_]*:.*for\s+[a-zA-Z_]", 
     "Comprehension dentro de f-string sem escaping - use {{ para {"),
    
    # {var: sem escape em f-string (pode ser confusão com formatação)
    (r"f['\"].*\{[a-zA-Z_][a-zA-Z0-9_]*\s*:",
     "Possível formatação em f-string - verifique se deveria usar {{"),
    
    # Dictionary comprehension com variáveis de loop
    (r"\{[a-zA-Z_][a-zA-Z0-9_]*:.*for\s+[a-zA-Z_]",
     "Dictionary comprehension - se dentro de f-string, use {{ e }}"),
]

def check_file_syntax(filepath):
    """Verifica se um arquivo Python tem sintaxe válida."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def analyze_file(filepath):
    """Analisa um arquivo em busca de padrões problemáticos."""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Erro ao ler arquivo: {e}"]
    
    lines = content.split('\n')
    
    # Verificar sintaxe primeiro
    valid_syntax, syntax_error = check_file_syntax(filepath)
    if not valid_syntax:
        issues.append(f"ERRO DE SINTAXE: {syntax_error}")
    
    # Procurar por padrões problemáticos
    for line_num, line in enumerate(lines, 1):
        # Ignora strings normais (não f-strings)
        if 'f"' not in line and "f'" not in line:
            continue
            
        # Procura comprehension dentro de f-strings
        # Padrão: f"... {k: ... for k in ...}"
        if 'for ' in line and ':' in line.split('for ')[0].split('{')[-1]:
            # Verifica se é dictionary comprehension
            match = re.search(r"\{([a-zA-Z_][a-zA-Z0-9_]*):.*for\s+([a-zA-Z_])", line)
            if match:
                # Verifica se está dentro de f-string
                fstring_start = line.find('f"')
                if fstring_start == -1:
                    fstring_start = line.find("f'")
                
                if fstring_start != -1:
                    # Verifica se as chaves estão escapadas
                    before_key = line[fstring_start:line.find('{')]
                    if '{{' not in before_key and '{' in before_key:
                        issues.append(
                            f"Linha {line_num}: Comprehension de dicionário dentro de f-string "
                            f"sem escaping correto: {line.strip()[:80]}..."
                        )
    
    return issues

def test_entity_generation():
    """Testa a geração de entidades para verificar se funciona."""
    print("\n" + "="*60)
    print("TESTE DE GERAÇÃO DE ENTIDADE")
    print("="*60)
    
    # Simula o código que estava causando erro
    entity_name = "Customer"
    domain = "customer"
    
    try:
        # Versão CORRETA (com escape)
        result = f'''"""Entity: {entity_name}"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class {entity_name}:
    """Domain entity for {domain}."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "{entity_name}":
        now = datetime.now()
        return {entity_name}(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}}
        )
    
    def to_dict(self) -> dict:
        return {{
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }}
'''
        # Tenta fazer parse do resultado
        ast.parse(result)
        print("✓ Geração de entidade funciona corretamente!")
        print(f"\nTrecho gerado:\n{result[:500]}...")
        return True
    except SyntaxError as e:
        print(f"✗ ERRO: {e}")
        return False

def scan_directory(directory):
    """Escaneia um diretório em busca de problemas."""
    print(f"\nEscaneando diretório: {directory}")
    print("="*60)
    
    all_issues = []
    
    for root, dirs, files in os.walk(directory):
        # Ignora diretórios específicos
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                issues = analyze_file(filepath)
                
                if issues:
                    print(f"\n📁 {filepath}")
                    for issue in issues:
                        print(f"   ⚠️  {issue}")
                        all_issues.append((filepath, issue))
    
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    if all_issues:
        print(f"Encontrados {len(all_issues)} problemas em {len(set(f for f, _ in all_issues))} arquivos")
    else:
        print("Nenhum problema encontrado!")
    
    return all_issues

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("DEBUG DE F-STRINGS")
    print("="*60)
    
    # Testa geração de entidade primeiro
    test_entity_generation()
    
    # Escaneia o diretório agents
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = "agents"
    
    issues = scan_directory(target_dir)
    
    # Sugestão de correção
    if issues:
        print("\n" + "="*60)
        print("COMO CORRIGIR")
        print("="*60)
        print("""
Se você tem um dicionário como:
    {k: v for k, v in items}

Dentro de uma f-string, você deve ESCAPAR as chaves:
    {{{k: v for k, v in items}}}

Isso transforma as chaves { } em literais { } na string resultante.
""")

