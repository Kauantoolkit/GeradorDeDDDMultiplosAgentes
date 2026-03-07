# Refactoring Plan: Self-Repair Architecture

## Current Architecture Problems

1. **Too many agents with fragmented context** - 8 agents that don't share state
2. **ValidatorAgent relies on LLM judgement** - Slow and subjective
3. **Runtime validation happens too late** - After validation, not in repair loop
4. **FixAgent doesn't receive full project context** - Only gets validation feedback
5. **Fragile JSON contracts between agents** - Complex parsing required everywhere
6. **State is distributed** - Hard to debug and trace

## Target Architecture

```
Orchestrator
    ↓
CodeAgent (generation + fixing with full context)
    ↓
RuntimeRunner (validates imports, syntax, startup)
    ↓
Self-repair loop (runtime errors → CodeAgent → retry)
```

## Implementation Steps

### Step 1: Create CodeAgent (merge Executor + Fix)
- **File:** `agents/code_agent.py`
- Combines code generation and fixing capabilities
- Receives full project files as context
- Responsible for both initial generation and error fixing

### Step 2: Enhance RuntimeRunner
- **File:** `agents/runtime_runner.py` (enhanced from runtime_validator.py)
- Objective validation: imports, syntax, startup
- Returns real errors and stack traces
- Integrated directly into the repair loop

### Step 3: Refactor Orchestrator
- **File:** `agents/orchestrator_v3.py`
- Simplified coordination logic
- Manages the self-repair loop
- Coordinates: generation → runtime validation → repair

### Step 4: Remove/Consolidate Redundant Agents
- Remove: ValidatorAgent (replaced by RuntimeRunner)
- Merge: ExecutorAgent + FixAgent → CodeAgent
- Keep: FrontendAgent (optional, can be called after backend is ready)
- Keep: RollbackAgent (for error recovery)

### Step 5: Update Domain Entities
- Add AgentType.CODE
- Update ExecutionResult to support both generation and fixing

## Key Principles

1. **Reduce agents** - From 8 to 3-4 main components
2. **Runtime-driven self-repair** - Use objective signals (import errors, syntax errors) instead of LLM judgment
3. **Full context for fixing** - CodeAgent receives all project files when fixing
4. **Simplified orchestration** - Orchestrator only coordinates flow
5. **Preserve functionality** - Don't simplify features, only architecture

## Files to Create/Modify

### New Files:
- `agents/code_agent.py` - Combined generation + fixing
- `agents/runtime_runner.py` - Enhanced runtime validation
- `agents/orchestrator_v3.py` - Simplified orchestrator

### Files to Remove:
- `agents/executor_agent.py` (merged into CodeAgent)
- `agents/fix_agent.py` (merged into CodeAgent)
- `agents/fix_agent_v2.py` (merged into CodeAgent)
- `agents/validator_agent.py` (replaced by RuntimeRunner)

### Files to Update:
- `domain/entities.py` - Add new agent types
- `agents/__init__.py` - Export new agents
- `main.py` - Use new orchestrator

## Testing Strategy

1. Test code generation still works
2. Test self-repair loop with intentional errors
3. Test runtime validation catches import errors
4. Test frontend generation still works

