import asyncio
import json
from infrastructure.llm_provider import OllamaProvider, PromptBuilder
from domain.entities import Requirement, ProjectConfig
from agents.code_agent import CodeAgent

async def test():
    # Setup
    config = ProjectConfig(
        output_directory='test_gen',
        model='llama3.2',
        framework='python-fastapi',
        database='postgresql',
        include_docker=False,
        include_tests=False
    )
    requirement = Requirement(
        description='Criar um clone do iFood com microservicos para pedidos, clientes, entregadores e pagamentos',
        project_config=config
    )
    
    # Get prompt
    prompt = PromptBuilder.build_executor_prompt(requirement)
    
    # Call LLM
    provider = OllamaProvider(model='llama3.2')
    print(f"Calling LLM with prompt ({len(prompt)} chars)...")
    result = await provider.generate(prompt, temperature=0.3, max_tokens=8000)
    
    print(f"LLM result: {len(result)} chars")
    print("First 1000 chars:")
    print(result[:1000])
    
    # Test parsing
    code_agent = CodeAgent(provider)
    parsed = code_agent._parse_llm_output(result)
    
    print(f"\nParsed result: {parsed}")
    
    if parsed:
        print("\nParsed microservices:", parsed.get('microservices', []))

asyncio.run(test())

