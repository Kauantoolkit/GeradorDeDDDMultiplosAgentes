# Refactoring TODO List

## Phase 1: Domain Updates
- [x] 1. Create REFACTORING_PLAN.md
- [x] 2. Update domain/entities.py - Add CODE agent type

## Phase 2: New Components
- [x] 3. Create agents/code_agent.py - Combined generation + fixing
- [x] 4. Create agents/runtime_runner.py - Enhanced runtime validation

## Phase 3: New Orchestrator
- [x] 5. Create agents/orchestrator_v3.py - Simplified orchestrator with self-repair loop

## Phase 4: Cleanup
- [x] 6. Update agents/__init__.py - Export new agents
- [x] 7. Update main.py - Use new orchestrator
- [x] 8. Deprecate old agents (kept for backward compatibility)

## Phase 5: Testing
- [ ] 9. Test the new architecture

## Summary

### New Architecture:
```
OrchestratorV3
    ↓
CodeAgent.generate() → files
    ↓
RuntimeRunner.validate() → errors?
    ↓
[Self-repair loop]
    while errors and attempts < MAX:
        CodeAgent.fix(errors) → modified files
        RuntimeRunner.validate() → errors?
    ↓
FrontendAgent (optional)
    ↓
Success
```

### Key Improvements:
1. **Fewer agents**: From 8 to 4 main components
2. **Runtime-driven repair**: Uses objective signals (import errors, syntax errors)
3. **Full context for fixing**: CodeAgent receives all project files when fixing
4. **Simplified orchestration**: Only coordinates generation, execution, repair loop

### Files Created:
- agents/code_agent.py - Unified generation + fixing
- agents/runtime_runner.py - Objective runtime validation
- agents/orchestrator_v3.py - Simplified orchestrator

### Files Modified:
- agents/__init__.py - Export new agents
- domain/entities.py - Added CODE, RUNTIME_RUNNER, FRONTEND agent types
- main.py - Uses OrchestratorV3

