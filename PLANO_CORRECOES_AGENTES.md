# Plano de Correções - Sistema de Agentes

## Análise dos Problemas

### 1. Duplicação de order_service
**Problema**: Existem duas localizações para order_service:
- `ifoodclone8/order_service/` (raiz)
- `ifoodclone8/services/order_service/` (serviços)

**Causa Raiz**: O Fix Agent cria NOVOS arquivos ao invés de corrigir os existentes, e não há normalização de caminhos entre Executor e Fix Agent.

### 2. Frontend Estático (não dinâmico)
**Problema**: O frontend gerado é um arquivo HTML estático simples em vez de uma aplicação React/Vue dinâmica.

**Causa Raiz**: O Executor gera apenas HTML estático, não detecta a necessidade de um frontend framework completo.

### 3. Agentes Não Validem/Corrigem Efetivamente
**Problema**: Você mencionou que consegue codar → validar → codar → rodar, mas seus agentes não fazem isso eficientemente.

**Causas Raizes Identificadas**:
1. **Executor**: Gera templates básicos sem lógica de negócio
2. **Validator**: Espera código de produção, não aceita templates
3. **Fix Agent**: Cria novos arquivos ao invés de corrigir existentes
4. **Falta de Loop de Validação Real**: O sistema não valida se o código realmente roda

---

## Plano de Correções

### FASE 1: Corrigir Duplicação de Arquivos

#### 1.1 Criar Normalizador de Caminhos
```
infrastructure/path_normalizer.py
```
- Normalizar `order-service` → `order_service`
- Normalizar caminhos entre agentes
- Garantir consistência de nomenclatura

#### 1.2 Modificar Fix Agent
```
agents/fix_agent.py
```
- ANTES de criar arquivo, verificar se já existe
- Se existe, fazer patch/modificação, não criar novo
- Adicionar lógica de "encontrar arquivo existente" antes de criar

#### 1.3 Script de Limpeza
```
scripts/cleanup_duplicates.py
```
- Detectar arquivos duplicados
- Manter apenas a versão mais completa
- Remover redundâncias

---

### FASE 2: Gerar Frontend Dinâmico

#### 2.1 Detectar Necessidade de Frontend
```
infrastructure/requirement_analyzer.py
```
- Analisar requisitos para detectar necessidade de frontend
- Identificar tipo de frontend (React, Vue, etc)
- Extrair entidades para CRUD dinâmico

#### 2.2 Modificar Executor para Gerar Frontend Completo
```
agents/executor_agent.py
```
- Gerar projeto React/Vue completo com package.json
- Gerar componentes dinâmicos baseados em entidades
- Gerar API de integração com backend

#### 2.3 Template de Frontend
```
templates/frontend/react/
templates/frontend/vue/
```
- Criar templates de frontend dinâmicos
- Componentes CRUD baseados em entidades
- Integração com API automática

---

### FASE 3: Melhorar Validação e Execução

#### 3.1 Adicionar Validação de Execução Real
```
agents/runtime_validator.py
```
- Tentar importar módulos Python
- Verificar syntax errors
- Testar se APIs sobem (sem banco)

#### 3.2 Melhorar o Validator Agent
```
agents/validator_agent.py
```
- Distinguir "template básico" de "código vazio"
- Não esperar código de produção de um gerador
- Aceitar templates DDD mínimos como válidos
- Ser mais flexível com placeholders

#### 3.3 Melhorar o Fix Agent
```
agents/fix_agent.py
```
- Primeiro: encontrar arquivo existente
- Segundo: aplicar patch no existente
- Terceiro: só criar novo se não existir
- Completar templates básicos com lógica de negócio

---

### FASE 4: Sistema de Retry Inteligente

#### 4.1 Retry com Validação
```
agents/orchestrator.py
```
- Após geração, VALIDAR EXECUÇÃO (não apenas estrutura)
- Se não executar, corrigir automaticamente
- Loop até executar ou limite atingido

#### 4.2 Detecção de Erros Comuns
```
agents/error_detector.py
```
- Detectar erros comuns automaticamente
- Aplicar correções determinísticas
- Só chamar LLM para erros complexos

---

## Implementação Sugerida

### Passo 1: Limpar projeto atual
```bash
# Remover duplicatas
python scripts/cleanup_duplicates.py ifoodclone8
```

### Passo 2: Aplicar correções nos agentes
```bash
# Atualizar normalizador de caminhos
# Atualizar Fix Agent para corrigir existentes
# Atualizar Validator para aceitar templates
```

### Passo 3: Testar fluxo completo
```bash
# Gerar novo projeto
python main.py --requirement "Sistema de delivery com frontend React"

# Validar se executa
python -c "from services.order_service.main import app"
```

---

## Métricas de Sucesso

| Métrica | Antes | Depois |
|---------|-------|--------|
| Arquivos duplicados | ✅ Presentes | ❌ Eliminados |
| Frontend | Estático HTML | React/Vue dinâmico |
| Código roda após geração | ❌ Não | ✅ Sim |
| Tentativas de correção | 3+ | 1-2 |
| Templates aceitos | ❌ Não | ✅ Sim |

---

## Próximos Passos

1. **CONFIRMAR**: Este plano resolve suas dores?
2. **IMPLEMENTAR**: Começar pela FASE 1 (mais simples)
3. **TESTAR**: Validar se sistema roda após correções
4. **ITERAR**: Ajustar conforme necessário

