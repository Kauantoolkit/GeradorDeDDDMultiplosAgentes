"""Test frontend validation"""
import asyncio
from agents.runtime_runner import RuntimeRunner, RuntimeRunnerOrchestrator

async def test():
    runner = RuntimeRunner(".")
    
    # Test current frontend
    result = await runner.validate_frontend()
    print(f"Frontend validation result:")
    print(f"  exists: {result.get('exists')}")
    print(f"  npm_install_ok: {result.get('npm_install_ok')}")
    print(f"  syntax_ok: {result.get('syntax_ok')}")
    print(f"  npm_build_ok: {result.get('npm_build_ok')}")
    print(f"  score: {result.get('score', 0):.2f}")
    if result.get('errors'):
        print(f"  errors: {result['errors'][:3]}")

if __name__ == "__main__":
    asyncio.run(test())

