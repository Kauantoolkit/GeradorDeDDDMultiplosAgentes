#!/usr/bin/env python3
"""
Sistema de Automação com Agentes para Geração de Microserviços DDD
==================================================================

Este sistema utiliza agentes AI para:
1. Analisar requisitos informados pelo usuário
2. Gerar automaticamente estruturas de microserviços com DDD
3. Validar se o código gerado atende aos requisitos
4. Fazer rollback em caso de falhas na validação

Uso:
    python main.py --requirements "Descrição dos requisitos"
    python main.py --interactive  # Modo interativo
"""

import argparse
import asyncio
import sys
from pathlib import Path
from loguru import logger

# Adiciona o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent
from domain.entities import Requirement, ProjectConfig
from infrastructure.llm_provider import OllamaProvider, ensure_ollama_running


def setup_logging():
    """Configura o sistema de logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/agent_system.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG"
    )


def parse_arguments():
    """Parseia os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sistema de Automação com Agentes para Geração de Microserviços DDD"
    )
    
    parser.add_argument(
        "--requirements", "-r",
        type=str,
        help="Descrição dos requisitos do projeto"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Modo interativo para informar requisitos"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="generated",
        help="Diretório de saída para o projeto gerado"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="llama3.2",
        help="Modelo Ollama a ser utilizado"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Modo verboso (debug)"
    )
    
    return parser.parse_args()


async def interactive_mode() -> str:
    """Modo interativo para coleta de requisitos."""
    print("\n" + "="*60)
    print("  SISTEMA DE GERAÇÃO DE MICROSSERVIÇOS DDD")
    print("="*60 + "\n")
    
    print("Descreva os requisitos do seu projeto:")
    print("(Exemplo: 'Criar um sistema de e-commerce com microserviços")
    print(" para gerenciamento de produtos, pedidos e usuários')\n")
    
    requirements = input("> ")
    
    print("\n--- Configurações Avançadas (opcional) ---")
    print("Pressione ENTER para usar os valores padrão\n")
    
    framework = input("Framework (python-fastapi/nodejs-nestjs) [padrão: python-fastapi]: ")
    if not framework.strip():
        framework = "python-fastapi"
    
    database = input("Banco de dados (postgresql/mongodb/mysql) [padrão: postgresql]: ")
    if not database.strip():
        database = "postgresql"
    
    return f"{requirements}\n\nConfigurações: framework={framework}, database={database}"


async def main():
    """Função principal do sistema."""
    args = parse_arguments()
    
    # Configura logging
    setup_logging()
    if args.verbose:
        logger.level = "DEBUG"
    
    logger.info("="*60)
    logger.info("  INICIANDO SISTEMA DE AGENTES")
    logger.info("="*60)
    
    # Coleta de requisitos
    if args.interactive:
        requirements_text = await interactive_mode()
    elif args.requirements:
        requirements_text = args.requirements
    else:
        logger.error("Informe os requisitos via --requirements ou use --interactive")
        sys.exit(1)
    
    logger.info(f"Requisitos recebidos: {requirements_text[:100]}...")
    
    # Configuração do projeto
    config = ProjectConfig(
        output_directory=args.output,
        model=args.model,
        framework="python-fastapi",  # Pode ser extraído dos requisitos
        database="postgresql"
    )
    
    # Requisito
    requirement = Requirement(
        description=requirements_text,
        project_config=config
    )
    
    # Garante que o Ollama está rodando
    logger.info("Verificando/Iniciando Ollama...")
    ensure_ollama_running()
    
    # Inicializa o provedor de LLM
    logger.info(f"Inicializando Ollama com modelo: {args.model}")
    llm_provider = OllamaProvider(model=args.model)
    
    # Inicializa o orquestrador
    orchestrator = OrchestratorAgent(llm_provider=llm_provider)
    
    # Executa o fluxo de agentes
    logger.info("Iniciando execução dos agentes...")
    result = await orchestrator.execute(requirement)
    
    # Resultado final
    print("\n" + "="*60)
    if result.success:
        print("  ✅ PROJETO GERADO COM SUCESSO!")
        print(f"  📁 Local: {result.project_path}")
        print(f"  📝 Microserviços: {', '.join(result.services)}")
    else:
        print("  ❌ FALHA NA GERAÇÃO DO PROJETO")
        print(f"  Erro: {result.error_message}")
        if result.rollback_performed:
            print("  ↩️ Rollback realizado automaticamente")
    print("="*60 + "\n")
    
    # Exibe os logs de execução incluindo o score
    print("--- Detalhes da Execução ---")
    for log in result.execution_logs:
        print(f"  {log}")
    print("="*60 + "\n")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nOperação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Erro fatal: {e}")
        sys.exit(1)
