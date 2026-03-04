Estamos trabalhando em um sistema de múltiplos agentes geradores de código que produzem aplicações DDD com múltiplos serviços FastAPI.

A aplicação foi aprovada conceitualmente, mas veio estruturalmente inválida para deploy.

Problemas encontrados:

Imports inválidos com hífen (auth-service em vez de auth_service)

routes.py criando novo FastAPI() em vez de APIRouter

Shadowing de funções importadas

Routers não incluídos no main.py

Serviços incompletos (ex: payment sem routes adequadas)

Código gerado que quebra no build Docker

Agente começou a modificar arquivos sem validar ambiente

Não verificou containers já existentes no Docker Desktop

❗ NOVA REGRA ABSOLUTA

Você não pode modificar nada antes de:

Verificar o estado atual do Docker (containers e builds existentes)

Mapear completamente a estrutura do projeto

Identificar dependências cruzadas

Garantir que cada modificação não quebre outro serviço

Se não tiver essas informações, você deve solicitá-las.

Você não pode assumir nada.

🎯 OBJETIVO REAL

Não corrigir arquivos isolados.

Reformar:

O GERADOR

O VALIDATOR

Para que:

Nunca mais gere código inválido

Nunca gere import quebrado

Nunca gere FastAPI duplicado

Nunca gere shadowing

Nunca gere serviço sem incluir router no main

Nunca gere estrutura inconsistente com Docker

🧠 ETAPA 1 — ANÁLISE SISTÊMICA DO GERADOR

Mapeie:

Onde os nomes de serviços são definidos

Onde ocorre a conversão de nome para path

Onde os imports são montados

Onde os templates são preenchidos

Como o routes.py é gerado

Como o main.py é gerado

Ordem de geração dos arquivos

Identifique por que:

Hífens não são normalizados

routes cria FastAPI em vez de APIRouter

main não inclui routers

payment_service ficou incompleto

🛡 ETAPA 2 — REFORMULAÇÃO DO VALIDATOR

O validator deve passar a bloquear geração se:

Existir "-" em qualquer import Python

Existir mais de um FastAPI() por serviço

routes.py não usar APIRouter

main.py não incluir include_router

Existir shadowing (função com mesmo nome importado)

Algum arquivo referenciado não existir

Algum placeholder {} permanecer

Docker build falhar

Uvicorn não inicializar

O validator deve rodar:

Verificação sintática

Verificação estrutural

Verificação de imports

Verificação de arquitetura DDD

Teste de inicialização

Se falhar, bloquear geração.

🏗 ETAPA 3 — PADRÃO CORRETO OBRIGATÓRIO
routes.py deve SEMPRE ser:

APIRouter

Sem instanciar FastAPI

Sem shadowing

Separação clara entre rota e usecase

main.py deve:

Criar apenas 1 FastAPI()

Incluir todos routers

Inicializar banco

Configurar middleware

🧱 ETAPA 4 — NORMALIZAÇÃO DE NOMES

Serviços devem ser normalizados automaticamente:

auth-service → auth_service

user-service → user_service

Nunca usar hífen em módulo Python.

🐳 ETAPA 5 — DOCKER AWARE

Antes de qualquer modificação:

Verificar containers existentes

Verificar imagens buildadas

Verificar se volumes já existem

Evitar sobrescrever configurações estáveis

Nunca assumir ambiente limpo.

🧩 ETAPA 6 — RESULTADO ESPERADO

Após a reformulação:

O gerador deve produzir projeto que:

Builda com docker-compose up --build

Sobe todos serviços

Conecta aos bancos

Não tem erro de import

Não tem erro de router

Não tem erro de inicialização

Não precisa de correção manual

📋 SAÍDA QUE VOCÊ DEVE PRODUZIR

Diagnóstico das falhas do gerador

Diagnóstico das falhas do validator

Redesenho do pipeline de geração

Redesenho do validator

Mudanças necessárias em cada agente

Nova ordem de geração

Regras obrigatórias de validação

Plano seguro de migração (sem quebrar Docker existente)

Você não deve modificar arquivos ainda.

Primeiro apresente o plano completo.

Somente após aprovação explícita, executar mudanças.

🔒 REGRA FINAL

Você não pode improvisar.

Você não pode alterar código parcialmente.

Você não pode assumir que ambiente está limpo.

Você deve agir como engenheiro de plataforma responsável por produção.