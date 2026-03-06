# Plano de correções – ciclo de geração do ifoodclone14

## 1) Leitura inicial e lacunas de contexto
- **Arquivo solicitado originalmente não encontrado:** `debug_ifood14.md`.
- **Atualização de contexto:** log completo foi recuperado e confirma pontos críticos adicionais no fluxo Executor → Validator → DockerTest → Fix.
- **Escopo analisado:** geração em `ifoodclone14/` e ciclo de agentes em `agents/`.

## 2) Diagnóstico do que foi gerado em `ifoodclone14`

### 2.1 Problemas funcionais no código gerado
1. **Handlers FastAPI com símbolos não importados** (`Request`, `User`, `Product`, `Payment`, `Address`, `Shipping`) causando falha em runtime.
2. **Rotas duplicadas com mesmo método + path** (ex.: `GET /api/payments`, `POST /api/shippings`) com risco de sobrescrita de handler.
3. **Estrutura de entrada inconsistente**: coexistem `services/main.py` e `services/<service>/main.py`.
4. **Diretório typo**: `infrastucture` coexistindo com `infrastructure`.
5. **Testes quebrados na coleta/import** por path inválido e empacotamento inconsistente.

### 2.2 Problemas de processo evidenciados no log recuperado
1. **Falso positivo de validação estrutural**:
   - validação manual aprova com score 1.0 mesmo com defeitos reais;
   - guardrails só reprovam por motivos periféricos (frontend/email), não pelo core quebrado.
2. **Extração incorreta de nomes de serviço no Validator**:
   - `services/api/...` e `services/main.py` entram como “serviços”, gerando leituras inválidas (ex.: `services/main.py/domain/...`).
3. **Regra de frontend excessivamente rígida**:
   - requisito “menciona frontend” vira bloqueio absoluto, mesmo quando entrega principal é backend.
4. **Parser JSON instável em Validator/FixAgent**:
   - respostas do LLM frequentemente não parseiam (`Expecting ',' delimiter`), degradando confiabilidade do ciclo.
5. **FixAgent com baixa efetividade na tentativa 2/3**:
   - tentativa 2 e 3 podem não aplicar alterações (0 arquivos), mas o ciclo continua consumindo tentativas sem convergência.
6. **Sinalização de “problemas” no Executor com ruído**:
   - `__init__.py` vazio/sem classes é tratado como problema, poluindo diagnóstico com não-críticos.

### 2.3 Evidência de validação local já levantada
- `python -m compileall ifoodclone14` passa (não detecta nomes indefinidos e conflitos de rota).
- `pytest -q ifoodclone14/services` falha na coleta com `ModuleNotFoundError`.

## 3) Causa-raiz provável por agente

### 3.1 Executor Agent
- Não possui **pré-gates semânticos bloqueantes** (AST, símbolos indefinidos, rotas duplicadas, typos de pasta).
- Aceita múltiplas fontes (`microservices`, `bounded_contexts`, `files`) sem política formal de conflito por path.
- Mistura alertas críticos e não-críticos no relatório final.

### 3.2 Validator Agent
- Dependência excessiva do LLM para score inicial, com fallback manual permissivo.
- Guardrails ainda não cobrem os erros mais caros (entrypoint, rotas, símbolos não importados).
- Extração de serviços não filtra arquivos (`main.py`) e namespaces técnicos (`services/api`).

### 3.3 FixAgent
- Falta política de “progresso mínimo”: se não altera arquivos críticos, deveria abortar cedo com causa explícita.
- Parser de resposta de correção precisa ser robustecido e validado antes de consumir tentativa.

### 3.4 Docker Test Agent / Orchestrator
- Docker roda mesmo com código já semanticamente inválido; falta **gate estático antes do build/up**.

## 4) Plano de correção proposto (priorizado)

## Fase A — Bloqueios imediatos (P0)
1. **Pré-validação estática no Executor (bloqueante):**
   - AST parse dos `.py` gerados;
   - detecção de símbolos não importados em handlers;
   - detecção de rotas duplicadas por método/path;
   - detecção de diretórios typo (`infrastucture`).
2. **Fail-fast com relatório estruturado P0** para acionar FixAgent com contexto preciso.
3. **Deduplicação e política de precedência por caminho** em `_create_project_files` (com log de conflito).

## Fase B — Guardrails determinísticos do Validator (P0)
1. Corrigir `_extract_service_names` para:
   - aceitar apenas `services/<nome>/...` com `<nome>` diretório válido;
   - ignorar `services/api` (namespace compartilhado) e qualquer item com sufixo de arquivo como `main.py`.
2. Novas regras objetivas:
   - conflitos de rota;
   - `Request` usado sem import;
   - símbolos usados em handlers sem definição/import;
   - validação de import path de testes.
3. **Frontend guardrail com modo explícito**:
   - só bloquear quando requisito exigir frontend como entregável obrigatório.

## Fase C — Robustez de parsing e contrato LLM (P0/P1)
1. Validator/FixAgent com parser resiliente (extração robusta + retries + JSON repair).
2. Se parsing falhar, **não aprovar por score alto manual sem checagens determinísticas mínimas**.
3. Contrato de saída mais rígido no prompt (schema mínimo e campos obrigatórios).

## Fase D — FixAgent orientado a convergência (P1)
1. Exigir **progresso mínimo por tentativa** (ex.: pelo menos 1 arquivo crítico alterado).
2. Auto-fixes prioritários:
   - imports FastAPI e símbolos de handler;
   - renomear `infrastucture -> infrastructure`;
   - resolver rotas duplicadas;
   - consertar imports de testes.
3. Se tentativa não produzir patch válido, encerrar cedo com motivo técnico (evita gastar 3 tentativas “vazias”).

## Fase E — Orquestração e qualidade de pipeline (P1)
1. Ordem de gates:
   - estático/semântico → validação funcional local → Docker.
2. Classificar findings por severidade (error/warn/info), evitando ruído de `__init__.py` vazio como erro crítico.
3. Suite mínima por serviço:
   - `python -m compileall services/<svc>`
   - `pytest -q services/<svc>/tests` (ou smoke test equivalente).

## 5) Ordem sugerida de implementação
1. Corrigir extração de serviços + frontend guardrail (impacto imediato no falso negativo/positivo).
2. Pré-gates semânticos do Executor.
3. Parser robusto em Validator/FixAgent.
4. FixAgent com critério de progresso mínimo.
5. Pipeline com gates antes do Docker + severidade de findings.

## 6) Critérios de pronto
- Nenhum serviço gerado com rota duplicada, símbolo indefinido ou import crítico ausente.
- Validator não tenta ler caminhos inválidos como `services/main.py/domain/...`.
- Reprovação por frontend ocorre apenas quando frontend for requisito mandatório.
- FixAgent não consome tentativas sem patch válido.
- Fluxo só chega no Docker quando validações estáticas e mínimas por serviço passarem.
