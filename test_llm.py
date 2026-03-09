import asyncio
import json
from infrastructure.llm_provider import OllamaProvider

async def test():
    provider = OllamaProvider(model='llama3.2')
    prompt = """Generate a simple JSON with microservices list. Return only JSON, no markdown."""
    
    result = await provider.generate(prompt, temperature=0.3, max_tokens=500)
    
    with open('llm_output.txt', 'w', encoding='utf-8') as f:
        f.write(result)
    print('Done, output length:', len(result))
    print('First 500 chars:', result[:500])

asyncio.run(test())

