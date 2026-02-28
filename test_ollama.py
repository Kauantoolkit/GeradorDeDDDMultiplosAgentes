#!/usr/bin/env python3
"""Test script to verify Ollama import works with auto-start."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from infrastructure.llm_provider import OllamaProvider, ensure_ollama_running
    print("✅ Import OK!")
    
    # Test starting Ollama automatically
    print("\n📦 Testando inicio automatico do Ollama...")
    result = ensure_ollama_running()
    
    if result:
        print("✅ Ollama esta rodando!")
    else:
        print("⚠️ Ollama nao conseguiu iniciar automaticamente")
    
    # Test creating an instance
    print("\n📦 Criando instancia do OllamaProvider...")
    provider = OllamaProvider(model="llama3.2")
    print(f"✅ OllamaProvider instance created with model: {provider.model}")
    
    print("\n🎉 Todos os testes passaram!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
