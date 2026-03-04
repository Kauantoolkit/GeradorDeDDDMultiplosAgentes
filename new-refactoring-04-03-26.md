🔎 CONTEXTO

Você está analisando um projeto gerado automaticamente por um sistema de múltiplos agentes geradores de código (arquitetura DDD + FastAPI + PostgreSQL + Docker).

O projeto gerado (ifood_clone) está estruturalmente bem organizado, porém não executa, pois contém:

Imports quebrados

Arquivos faltando

Templates não populados

Classes malformadas

Serviços parcialmente implementados

main.py incompleto

Placeholders não substituídos

Sua missão NÃO é apenas corrigir esse projeto específico.

Sua missão é:

Refatorar o GERADOR para que ele nunca mais produza projetos que não executam.

🎯 OBJETIVO

Transformar o gerador para que ele entregue aplicações 100% executáveis via:

docker-compose up --build

Sem necessidade de correções manuais.

📋 ETAPAS OBRIGATÓRIAS DA ANÁLISE
1️⃣ Análise Estrutural Completa

Mapeie:

Estrutura de pastas

Responsabilidades de cada agente

Ordem de geração dos arquivos

Dependências cruzadas entre agentes

Pontos onde placeholders não são substituídos

Pontos onde arquivos são assumidos mas não criados

2️⃣ Detectar Problemas Sistêmicos do Gerador

Identifique padrões como:

Geração de imports antes da criação dos arquivos

Uso de nomes inconsistentes (order vs orders_entities)

Uso de templates com {entity_name} não resolvidos

Arquivos esperados mas nunca gerados

Confusão entre camadas (use_cases em domain ao invés de application)

3️⃣ Redesenhar Fluxo do Gerador

Proponha uma nova ordem de geração:

Domain (entities + value objects)

Domain interfaces (repositories)

Application (use_cases)

Infrastructure (database, repositories, services)

API (schemas, routers)

main.py

docker-compose

Migrations

4️⃣ Criar Checklist de Integridade Automática

O gerador só pode finalizar se:

Todos imports existirem

Nenhum placeholder {} permanecer

Todos arquivos referenciados existirem

Todos serviços subirem sem erro de import

main.py inicializar FastAPI corretamente

Repositórios implementarem interfaces

Docker build não quebrar

Implemente uma etapa de validação automática antes de concluir a geração.

5️⃣ Corrigir Arquitetura DDD

Garanta:

domain = regras de negócio puras

application = casos de uso

infrastructure = implementações concretas

api = camada HTTP

main.py = composição e bootstrap

Nunca misturar camadas.

6️⃣ Melhorias Estruturais no Gerador

Implemente:

Sistema de substituição real de templates

Validador de imports

Gerador de migrations

Geração automática de dependências

Teste automático de inicialização do projeto

7️⃣ Resultado Esperado

Ao final, o gerador deve ser capaz de:

Criar um projeto DDD multi-serviço

Subir todos os containers

Conectar ao banco

Criar tabelas

Expor endpoints funcionais

Executar sem erro de import

📊 SAÍDA QUE VOCÊ DEVE PRODUZIR

Sua resposta deve conter:

Diagnóstico das falhas do gerador

Falhas arquiteturais

Redesenho do fluxo de geração

Plano de refatoração do sistema de agentes

Melhorias estruturais

Checklist de validação automática

Mudanças necessárias em cada agente

Não faça apenas correções pontuais.

Faça engenharia reversa do problema e torne o gerador confiável.