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
import shutil

# Adiciona o caminho do Ollama ao PATH se não estiver
def _setup_ollama_path():
    """Adiciona o Ollama ao PATH do sistema se necessário."""
    # Primeiro, tenta encontrar o Ollama no sistema
    ollama_path = shutil.which("ollama")
    
    if ollama_path:
        # Encontrou o Ollama no PATH, usa o diretório onde está
        ollama_dir = os.path.dirname(ollama_path)
        logger.info(f"Ollama encontrado em: {ollama_dir}")
        return ollama_dir
    
    # Se não encontrou, tenta os caminhos comuns de instalação
    possible_paths = [
        r"C:\Users\kauan\AppData\Local\Programs\ollama",
        r"C:\Program Files\ollama",
        os.path.expanduser(r"~\AppData\Local\Programs\ollama"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            ollama_exe = os.path.join(path, "ollama.exe")
            if os.path.exists(ollama_exe):
                logger.info(f"Ollama encontrado em: {path}")
                # Adiciona ao PATH
                if path not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")
                return path
    
    # Não encontrou, retorna o caminho padrão para tentar iniciar mesmo assim
    default_path = r"C:\Users\kauan\AppData\Local\Programs\ollama"
    logger.warning(f"Ollama não encontrado no sistema. Tentará usar: {default_path}")
    return default_path

# Executa a configuração do PATH ao importar o módulo
_OLLAMA_PATH = _setup_ollama_path()


def check_ollama_installation() -> bool:
    """
    Verifica se o Ollama está instalado no sistema.
    
    Returns:
        True se o Ollama está instalado, False caso contrário
    """
    import shutil
    
    # Primeiro, tenta encontrar o Ollama no PATH do sistema
    ollama_path = shutil.which("ollama")
    
    if ollama_path:
        logger.info(f"Ollama encontrado em: {ollama_path}")
        return True
    
    # Se não encontrou no PATH, verifica nos caminhos comuns de instalação no Windows
    possible_paths = [
        r"C:\Users\kauan\AppData\Local\Programs\ollama\ollama.exe",
        r"C:\Program Files\ollama\ollama.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\ollama\ollama.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Ollama encontrado em: {path}")
            return True
    
    logger.warning("Ollama não encontrado no sistema")
    return False


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
    
    def __init__(self, model: str = "qwen2.5-coder", base_url: str = "http://localhost:11434"):
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
        # Se modo DDD está habilitado, usar prompts DDD
        if hasattr(requirement, 'use_ddd_mode') and requirement.use_ddd_mode:
            return PromptBuilder.build_ddd_executor_prompt(requirement)
        
        # Modo legado
        base_prompt = requirement.to_prompt()
        
        # Use chr to avoid backtick issues
        bt = chr(96)
        triple_bt = bt * 3
        
        return """
Você é o AGENTE EXECUTOR de um sistema de automação de geração de código DDD.

SUA FUNÇÃO CRÍTICA:
- Analisar os requisitos fornecidos com MUITA ATENÇÃO
- Identificar TODOS os microserviços necessários
- Gerar a estrutura COMPLETA de diretórios DDD com TODAS as camadas
- Criar TODOS os arquivos de código fonte necessários
- NADA pode ficar faltando - seja EXTENSO e COMPLETO

ARQUITETURA DDD OBRIGATÓRIA (para CADA microserviço):

services/
  [nome_servico]/
    domain/
      __init__.py
      entities.py
      value_objects.py
      aggregates.py
      events.py
    application/
      __init__.py
      use_cases.py
      dtos.py
      mappers.py
    infrastructure/
      __init__.py
      repositories.py
      database.py
    api/
      __init__.py
      routes.py
      controllers.py
      schemas.py
    main.py
    requirements.txt
    Dockerfile
    docker-compose.yml
    tests/
      __init__.py
      test_entities.py

IMPORTANTE - FORMATO DE RESPOSTA:
Você DEVE retornar APENAS um objeto JSON válido.

CRÍTICO - EVITE ESTES ERROS:
1. NÃO use markdown como ```json
2. NÃO inclua comentários no JSON
3. NÃO use aspas simples
4. NÃO deixe vírgulas antes de }} ou ]
5. SEMPRE inicie com {{ e termine com }}

{base_prompt}

Retorne um JSON com esta estrutura:

{{
    "microservices": [
        {{
            "name": "nome_do_servico",
            "domain": "nome_do_dominio",
            "entities": ["Entity1", "Entity2"],
            "use_cases": ["UseCase1", "UseCase2"],
            "ports": ["/api/endpoint1", "/api/endpoint2"],
            "dependencies": ["outro_servico"]
        }}
    ],
    "files": [
        {{
            "path": "caminho/para/arquivo.py",
            "content": "conteúdo completo do arquivo"
        }}
    ]
}}

GARANTA QUE:
- O JSON seja válido
- Crie NO MÍNIMO 5 arquivos por microserviço
- Inclua TODAS as camadas DDD
- Cada arquivo tenha código real
- NÃO use markdown
""".format(base_prompt=base_prompt)
    
    @staticmethod
    def build_ddd_executor_prompt(requirement: Any) -> str:
        """
        Constrói o prompt DDD estratégico para o Executor Agent.
        
        Este prompt força a geração de código com modelagem de domínio rica,
        agregados consistentes e separação rigorosa de camadas.
        
        Args:
            requirement: Requisito do projeto com bounded contexts
            
        Returns:
            Prompt formatado para DDD
        """
        config = requirement.project_config
        
        # Constrói informações dos bounded contexts
        contexts_prompt = ""
        if hasattr(requirement, 'bounded_contexts') and requirement.bounded_contexts:
            for ctx in requirement.bounded_contexts:
                contexts_prompt += f"""
=== BOUNDED CONTEXT: {ctx.name} ===
Aggregate Root: {ctx.aggregate_root}
"""
                if ctx.entities:
                    contexts_prompt += f"Entities: {', '.join([e.name for e in ctx.entities])}\n"
                if ctx.value_objects:
                    contexts_prompt += f"Value Objects: {', '.join([vo.name for vo in ctx.value_objects])}\n"
                if ctx.domain_services:
                    contexts_prompt += f"Domain Services: {', '.join([ds.name for ds in ctx.domain_services])}\n"
                if ctx.domain_events:
                    contexts_prompt += f"Domain Events: {', '.join([de.name for de in ctx.domain_events])}\n"
                if ctx.use_cases:
                    contexts_prompt += f"Use Cases: {', '.join([uc.name for uc in ctx.use_cases])}\n"
        
        bt = chr(96)
        triple_bt = bt * 3
        
        return f"""
Você é o AGENTE EXECUTOR DDD (Domain-Driven Design).
Sua missão é gerar Bounded Contexts completos com modelagem de domínio estratégica e tática.

REQUISITOS: {requirement.description}

CONFIGURAÇÕES:
- Framework: {config.framework}
- Banco de Dados: {config.database}
- Diretório: {config.output_directory}
- Incluir Tests: {config.include_tests}
- Incluir Docker: {config.include_docker}

{contexts_prompt}

══════════════════════════════════════════════════════════════
ESTRUTURA OBRIGATÓRIA - CLEAN ARCHITECTURE + DDD
══════════════════════════════════════════════════════════════

Para CADA Bounded Context, gere:

/domain                    # CAMADA DE DOMÍNIO - SEM DEPENDÊNCIAS EXTERNAS
  /entities/               # Entidades com comportamento (não anêmicas!)
    __init__.py
    [EntityName].py        # Ex: Invoice.py, Order.py, User.py
      - deve ter métodos com REGRAS DE NEGÓCIO
      - NÃO apenas getters/setters
  /value_objects/          # Value Objects imutáveis com validação
    __init__.py
    [ValueObjectName].py  # Ex: Money.py, Address.py, Email.py
      - deve ter __post_init__ com validação
      - deve ter métodos de domínio (add, multiply, etc)
  /aggregates/             # Aggregate Roots controlando invariantes
    __init__.py
    [AggregateName].py     # Ex: InvoiceAggregate.py
      - encapsula entidades e value objects
      - controla INVARIANTES de negócio
      - não permite acesso direto às entidades internas
  /events/                 # Domain Events
    __init__.py
    [EventName].py         # Ex: InvoiceCreatedEvent.py
  /repositories/           # Interfaces (protocolos) - APENAS interfaces!
    __init__.py
    [EntityName]Repository.py  # Interface, não implementação

/application               # CAMADA DE APLICAÇÃO
  /use_cases/              # Orchestra agregados
    __init__.py
    [UseCaseName].py       # Ex: CreateInvoiceUseCase.py
      - Recebe DTO
      - Orquestra agregados
      - Dispara eventos
      - NÃO tem regras de negócio (apenas fluxo)
  /dto/                    # Data Transfer Objects
    __init__.py
    [EntityName]DTO.py
  /ports/                  # Interfaces para serviços externos
    __init__.py
    [PortName].py

/infrastructure           # CAMADA DE INFRAESTRUTURA - IMPLEMENTAÇÕES
  /persistence/           # Entity Framework / SQLAlchemy models
    __init__.py
    [EntityName]Model.py   # ORM entities - NUNCA importe no domínio!
  /repositories/           # Implementações concretas
    __init__.py
    [EntityName]RepositoryImpl.py
  /mappers/                # Mapping between domain and infrastructure
    __init__.py
    [EntityName]Mapper.py
  /database.py             # Configuração de banco

/api                       # CAMADA DE APRESENTAÇÃO
  /controllers.py          # Adaptadores de entrada
  /routes.py               # Rotas FastAPI
  /schemas.py              # Pydantic schemas

/tests                     # TESTES DE DOMÍNIO (sem banco, sem frameworks)
  /domain/
    test_[aggregate].py    # Testa invariantes, regras
  /use_cases/
    test_[use_case].py    # Testa orchestração

══════════════════════════════════════════════════════════════
REGRAS DDD OBRIGATÓRIAS
══════════════════════════════════════════════════════════════

1. DOMÍNIO NUNCA PODE IMPORTAR FRAMEWORKS
   - sqlalchemy, fastapi, pydantic são INFRAESTRUTURA
   - domain/entities.py deve importar APENAS built-ins (uuid, datetime, dataclasses)

2. ENTIDADES NÃO PODEM SER ANÊMICAS
   - ERRADO: class User:
       id: str
       nome: str
       def get_nome(self): return self.nome
   
   - CORRETO: class User:
       id: str
       _nome: str  # private
       def change_name(self, novo_nome):
           if not novo_nome: raise DomainException("Nome inválido")
           self._nome = novo_nome

3. VALUE OBJECTS SÃO IMUTÁVEIS
   - Usar @dataclass(frozen=True)
   - Validações no __post_init__
   - Métodos retornam NOVAS instâncias

4. AGGREGATE ROOT CONTROLA INVARIANTES
   - Nenhuma entidade interna pode ser acessada diretamente
   - Todas as modificações passam pela raiz
   - Invariantes verificadas em CADA mudança

5. DOMAIN EVENTS PARA REAÇÕES EM CADEIA
   - Criar eventos quando algo significativo acontece
   - Eventos são usados por Application Layer para reações

6. USE CASES ORQUESTRAM (NÃO TÊM REGRAS)
   - Use case busca agregados
   - Chama métodos do agregado (que têm as regras)
   - Dispara eventos
   - Salva

══════════════════════════════════════════════════════════════
FORMATO DE RESPOSTA
══════════════════════════════════════════════════════════════

Retorne APENAS JSON válido:
{{
    "bounded_contexts": [
        {{
            "name": "billing",
            "files": [
                {{"path": "services/billing/domain/entities/invoice.py", "content": "..."}},
                {{"path": "services/billing/domain/value_objects/money.py", "content": "..."}},
                {{"path": "services/billing/domain/aggregates/invoice_aggregate.py", "content": "..."}},
                {{"path": "services/billing/domain/events/invoice_created_event.py", "content": "..."}},
                {{"path": "services/billing/domain/repositories/invoice_repository.py", "content": "..."}},
                {{"path": "services/billing/application/use_cases/create_invoice_use_case.py", "content": "..."}},
                {{"path": "services/billing/application/dto/create_invoice_dto.py", "content": "..."}},
                {{"path": "services/billing/infrastructure/persistence/invoice_model.py", "content": "..."}},
                {{"path": "services/billing/infrastructure/repositories/invoice_repository_impl.py", "content": "..."}},
                {{"path": "services/billing/api/routes.py", "content": "..."}},
                {{"path": "services/billing/main.py", "content": "..."}}
            ]
        }}
    ]
}}

GARANTA QUE CADA ARQUIVO TENHA:
- Código Python REAL e FUNCIONAL (não placeholders)
- Imports corretos (domínio só importa domínio!)
- Regras de negócio no lugar certo
- Sem dependência circular
- O JSON seja válido e retornado SEM markdown (sem {triple_bt})
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
Você é o AGENTE VALIDADOR de um sistema de automação de geração de código DDD.

SUA FUNÇÃO CRÍTICA:
- Validar se o código gerado atende aos requisitos originais
- Verificar se a estrutura DDD está COMPLETA para cada microserviço
- Identificar problemas e inconsistências específicas
- Decidir se aprova ou reprova o código gerado
- Dar feedback SPECÍFICO sobre o que falta

REQUISITOS ORIGINAIS (analise com ATENÇÃO):
{requirement.description}

CONFIGURAÇÕES DO PROJETO:
- Framework: {requirement.project_config.framework}
- Banco de Dados: {requirement.project_config.database}

ARQUIVOS CRIADOS:
{chr(10).join([f"- {f}" for f in execution_result.files_created[:50]]) if execution_result.files_created else "Nenhum arquivo encontrado"}

CÓDIGO GERADO (analise os arquivos):
{execution_result.output[:8000]}

INSTRUÇÕES DE VALIDAÇÃO DETALHADA:

1. ESTRUTURA DDD - Para cada microserviço, verifique cada camada:
   - domain/entities.py existe e tem classes Python reais? (não vazio)
   - domain/__init__.py existe?
   - application/use_cases.py existe e tem funções? (não vazio)
   - application/__init__.py existe?
   - infrastructure/repositories.py existe e tem classes?
   - infrastructure/__init__.py existe?
   - api/routes.py existe e tem rotas FastAPI?
   - api/__init__.py existe?
   - main.py existe?

2. QUALIDADE DO CÓDIGO:
   - Código tem classes/funções reais ou está vazio?
   - Imports estão corretos?
   - Há código boilerplate ou código funcional?

3. COMPLETUDE:
   - Se os requisitos pedem "usuário", existe entidade User?
   - Se os requisitos pedem "login", existe use case de autenticação?
   - Se os requisitos pedem "API REST", existem rotas definidas?

4. PREFERÊNCIA PARA APROVAR se:
   - A estrutura DDD está presente
   - Há código real (não apenas placeholders)
   - Os arquivos principais existem

Retorne em formato JSON com análise específica:
{{
    "status": "approved" | "rejected",
    "score": 0.0-1.0,
    "approved_items": ["item1 implementado corretamente"],
    "rejected_items": ["item1 faltando ou vazio"],
    "missing_items": ["arquivo/funcionalidade que falta"],
    "issues": ["problema específico encontrado"],
    "feedback": "explique o que está faltando ou correto de forma específica"
}}

Gere APENAS o JSON, sem texto adicional.
"""
    
    @staticmethod
    def build_fix_prompt(
        requirement: Any,
        validation_result: Any,
        execution_result: Any,
        file_context: str = "",
    ) -> str:
        """
        Constrói o prompt para o Fix Agent - Versão melhorada.
        
        Args:
            requirement: Requisito original
            validation_result: Resultado da validação com problemas
            execution_result: Resultado da execução do Executor
            
        Returns:
            Prompt formatado
        """
        # Coleta problemas específicos
        issues = []
        issues.extend(validation_result.issues)
        for item in validation_result.rejected_items:
            issues.append(f"Rejeitado: {item}")
        for item in validation_result.missing_items:
            issues.append(f"Faltando: {item}")
        
        issues_text = "\n".join([f"- {issue}" for issue in issues])
        
        files_list = "\n".join([f"- {f}" for f in execution_result.files_created[:30]]) if execution_result.files_created else "Nenhum arquivo"
        
        return f"""
Você é o AGENTE DE CORREÇÃO de um sistema de automação de geração de código DDD.

SUA FUNÇÃO CRÍTICA:
- Analisar os problemas identificados pelo validador
- Corrigir os arquivos existentes ou criar novos
- Tornar o código COMPLETO e FUNCIONAL

REQUISITOS ORIGINAIS:
{requirement.description}

PROBLEMAS IDENTIFICADOS PELO VALIDADOR:
{issues_text}

ARQUIVOS JÁ CRIADOS:
{files_list}

SNIPPETS DE ARQUIVOS RELEVANTES (para editar com precisão):
{file_context or "(sem snippets disponíveis)"}

CÓDIGO ATUAL:
{execution_result.output[:6000]}

INSTRUÇÕES PARA CORREÇÃO:

1. Para CADA problema identificado, você DEVE:
   - Identificar qual arquivo precisa criar/modificar
   - Gerar código COMPLETO e FUNCIONAL
   - Não criar placeholders ou código vazio

2. EXEMPLOS DE CORREÇÕES:

   Se "entities faltando":
   - Crie domain/entities.py com classes reais

   Se "use_cases faltando":
   - Crie application/use_cases.py com funções reais

   Se "routes faltando":
   - Crie api/routes.py com rotas FastAPI reais

3. Estrutura DDD para cada microserviço:
   - domain/entities.py - Entidades
   - domain/__init__.py - Exports
   - application/use_cases.py - Casos de uso
   - application/__init__.py - Exports
   - infrastructure/repositories.py - Repositories
   - infrastructure/__init__.py - Exports
   - api/routes.py - Rotas
   - api/__init__.py - Exports
   - main.py - Entry point

Retorne em formato JSON:
{{
    "fixes": [
        {{
            "file_path": "services/nome_servico/domain/entities.py",
            "action": "create" | "modify" | "patch",
            "content": "código completo do arquivo",
            "search": "trecho antigo exato (somente para action=patch)",
            "replace": "trecho novo (somente para action=patch)",
            "reason": "por que esta correção resolve o problema"
        }}
    ]
}}

GARANTA QUE:
- Crie código COMPLETO, não placeholders
- Use nomes que fazem sentido
- O código deve ser syntacticamente correto
- Retorne APENAS o JSON, sem markdown
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
