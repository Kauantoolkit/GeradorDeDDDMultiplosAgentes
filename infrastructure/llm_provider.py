"""
Provedor de LLM - Conexão com Ollama
=====================================

Este módulo fornece a interface para comunicação com o Ollama
(LLM local) para geração de código pelos agentes.
"""

import json
import asyncio
import os
from typing import Any
from loguru import logger
from ollama import AsyncClient


import subprocess

# Adiciona o caminho do Ollama ao PATH se não estiver
def _setup_ollama_path():
    """Adiciona o Ollama ao PATH do sistema se necessário."""
    ollama_path = r"C:\Users\kauan\AppData\Local\Programs\ollama"
    if ollama_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ollama_path + os.pathsep + os.environ.get("PATH", "")
        logger.info(f"Ollama adicionado ao PATH: {ollama_path}")
    return ollama_path

# Executa a configuração do PATH ao importar o módulo
_OLLAMA_PATH = _setup_ollama_path()


def ensure_ollama_running():
    """
    Garante que o Ollama está rodando. Se não estiver, inicia automaticamente.
    """
    import socket
    import time
    
    # Verifica se já está rodando na porta 11434
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 11434))
    sock.close()
    
    if result == 0:
        logger.info("Ollama já está rodando!")
        return True
    
    # Se não estiver rodando, tenta iniciar
    logger.info("Iniciando Ollama automaticamente...")
    ollama_exe = os.path.join(_OLLAMA_PATH, "ollama.exe")
    
    try:
        # Inicia o servidor Ollama em segundo plano
        subprocess.Popen(
            [ollama_exe, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Espera até que o servidor esteja pronto
        for _ in range(30):
            time.sleep(1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            if result == 0:
                logger.info("Ollama iniciado com sucesso!")
                return True
        
        logger.warning("Ollama iniciou mas não ficou pronto a tempo")
        return False
        
    except Exception as e:
        logger.error(f"Erro ao iniciar Ollama: {e}")
        return False


class LLMProvider:
    """Classe base para provedores de LLM."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Gera texto a partir de um prompt."""
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """
    Provedor de LLM usando Ollama.
    
    Gerencia a conexão com o Ollama local e fornece
    métodos para geração de código.
    """
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        """
        Inicializa o provedor Ollama.
        
        Args:
            model: Nome do modelo a ser usado
            base_url: URL base do servidor Ollama
        """
        self.model = model
        self.base_url = base_url
        self.client = AsyncClient(host=base_url)
        logger.info(f"OllamaProvider inicializado com modelo: {model}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """
        Gera texto usando o Ollama.
        
        Args:
            prompt: Prompt com instruções para o modelo
            temperature: Temperatura para geração (0.0 - 1.0)
            max_tokens: Número máximo de tokens a gerar
            
        Returns:
            Texto gerado pelo modelo
        """
        try:
            logger.debug(f"Enviando prompt para {self.model} ({len(prompt)} chars)")
            
            # Passa temperature e max_tokens via options (API correta do Ollama)
            options = {
                'temperature': temperature,
                'num_predict': max_tokens,
            }
            
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                options=options,
                stream=False,
                **kwargs
            )
            
            result = response.response
            logger.debug(f"Resposta recebida ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao chamar Ollama: {e}")
            raise
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        """
        Gera resposta em formato de chat.
        
        Args:
            messages: Lista de mensagens no formato [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
            
        Returns:
            Resposta do modelo
        """
        try:
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.message.content
        except Exception as e:
            logger.error(f"Erro no chat com Ollama: {e}")
            raise
    
    async def check_connection(self) -> bool:
        """
        Verifica se o Ollama está acessível.
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            await self.client.list()
            logger.info("Conexão com Ollama estabelecida")
            return True
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Ollama: {e}")
            return False
    
    async def list_models(self) -> list[str]:
        """
        Lista os modelos disponíveis no Ollama.
        
        Returns:
            Lista de nomes dos modelos
        """
        try:
            models = await self.client.list()
            return [m.model for m in models.models]
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []


class PromptBuilder:
    """
    Constrói prompts estruturados para os agentes.
    """
    
    @staticmethod
    def build_executor_prompt(requirement: Any) -> str:
        """
        Constrói o prompt para o Executor Agent.
        
        Args:
            requirement: Requisito do projeto
            
        Returns:
            Prompt formatado
        """
        base_prompt = requirement.to_prompt()
        
        # Use chr to avoid backtick issues
        bt = chr(96)
        triple_bt = bt * 3
        
        return f"""
Você é o AGENTE EXECUTOR de um sistema de automação de geração de código.

SUA FUNÇÃO:
- Analisar os requisitos fornecidos
- Identificar os microserviços necessários
- Gerar a estrutura completa de diretórios DDD
- Criar os arquivos de código fonte

IMPORTANTE - FORMATO DE RESPOSTA:
Você DEVE retornar APENAS um objeto JSON válido, sem nenhum texto adicional antes ou depois.
Não inclua explicações, introduções ou conclusões em texto.
O JSON deve ser compacto (sem formatação pretty-print com espaços extras).

{base_prompt}

Retorne um JSON válido com esta estrutura exata:
{{
    "microservices": [
        {{
            "name": "nome-do-servico",
            "domain": "nome-do-dominio",
            "entities": ["Entity1", "Entity2"],
            "use_cases": ["UseCase1", "UseCase2"],
            "ports": ["/api/endpoint1", "/api/endpoint2"],
            "dependencies": ["outro-servico"]
        }}
    ],
    "files": [
        {{
            "path": "caminho/para/arquivo.py",
            "content": "conteúdo do arquivo"
        }}
    ]
}}

GARANTA QUE:
- O JSON seja válido e possa ser parseado
- Todas as strings usem aspas duplas "
- Não haja trailing commas (vírgulas extras)
- Não haja comentários no JSON
- O JSON seja retornado SEM formatação markdown (sem {triple_bt}json ou {triple_bt})
"""
    
    @staticmethod
    def build_validator_prompt(requirement: Any, execution_result: Any) -> str:
        """
        Constrói o prompt para o Validator Agent.
        
        Args:
            requirement: Requisito original
            execution_result: Resultado da execução do Executor
            
        Returns:
            Prompt formatado
        """
        return f"""
Você é o AGENTE VALIDADOR de um sistema de automação de geração de código.

SUA FUNÇÃO:
- Validar se o código gerado atende aos requisitos originais
- Verificar se a estrutura DDD está correta
- Identificar problemas e inconsistências
- Decidir se aprova ou reprova o código gerado

REQUISITOS ORIGINAIS:
{requirement.description}

CONFIGURAÇÕES:
- Framework: {requirement.project_config.framework}
- Banco de Dados: {requirement.project_config.database}

CÓDIGO GERADO:
{execution_result.output[:5000]}  # Primeiros 5000 chars

INSTRUÇÕES DE VALIDAÇÃO:
1. Compare o código gerado com os requisitos
2. Verifique se todos os domínios identificados estão implementados
3. Confirme que a estrutura DDD está completa
4. Identifique partes faltantes ou incorretas
5. Dê uma nota de 0.0 a 1.0 para a qualidade

Retorne em formato JSON:
{{
    "status": "approved" | "rejected",
    "score": 0.0-1.0,
    "approved_items": ["item1", "item2"],
    "rejected_items": ["item1", "item2"],
    "missing_items": ["item1"],
    "issues": ["problema1", "problema2"],
    "feedback": "feedback geral"
}}

Gere APENAS o JSON, sem texto adicional.
"""
    
    @staticmethod
    def build_rollback_prompt(files_to_rollback: list[str]) -> str:
        """
        Constrói o prompt para o Rollback Agent.
        
        Args:
            files_to_rollback: Lista de arquivos para remover
            
        Returns:
            Prompt formatado
        """
        files_list = "\n".join(f"- {f}" for f in files_to_rollback)
        
        return f"""
Você é o AGENTE ROLLBACK de um sistema de automação de geração de código.

SUA FUNÇÃO:
- Remover todos os arquivos criados pelo Executor Agent
- Garantir que o diretório volte ao estado anterior
- Limpar qualquer estado residual

ARQUIVOS A REMOVER:
{files_list}

INSTRUÇÕES:
1. Remova cada arquivo listados acima
2. Remova diretórios vazios
3. Confirme a remoção de cada arquivo
4. Retorne um relatório das remoções

Retorne em formato JSON:
{{
    "status": "success" | "failed",
    "files_removed": ["file1", "file2"],
    "errors": ["erro1"],
    "message": "mensagem de confirmação"
}}

Gere APENAS o JSON, sem texto adicional.
"""
