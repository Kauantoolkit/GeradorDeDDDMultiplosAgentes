#!/usr/bin/env python3
"""Check available Ollama models."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.llm_provider import OllamaProvider

async def check():
    p = OllamaProvider()
    models = await p.list_models()
    print('Available models:', models)

asyncio.run(check())

