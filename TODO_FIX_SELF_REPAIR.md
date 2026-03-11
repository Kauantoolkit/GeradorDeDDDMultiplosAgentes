# TODO: Fix Self-Repair Loop After Database Creation

## Problem
The cycle of testing the app and fixing is not happening because:
1. `orchestrator_v3.py` returns early after database creation, never reaching the self-repair loop
2. `api/server.py` `continue_generation` only validates but never calls CodeAgent to fix errors

## Plan

### Step 1: Fix `api/server.py` - Add self-repair loop to `continue_generation` ✅
- Add import for CodeAgent
- Implement validation → fix → re-validate loop (up to 5 attempts)
- Send progress updates via WebSocket

### Step 2: Test the fix
- Run the API and test the full flow
- Verify errors are detected and fixed

## Status: COMPLETED ✅

### Changes Made to `api/server.py`:
1. Modified `continue_generation` function to include self-repair loop:
   - Gets LLM provider from pending_tasks
   - Creates CodeAgent instance
   - Loops up to 5 times:
     - Validates services with RuntimeRunner
     - If errors found, calls CodeAgent.fix() with runtime errors
     - Re-validates after each fix attempt
   - Sends detailed progress updates via WebSocket
   - Reports final status (success or with remaining issues)

### New Flow:
```
User clicks "Continue"
    ↓
validate_and_fix() → errors?
    ↓ (if errors)
CodeAgent.fix(errors)
    ↓
validate_and_fix() → errors? (loop up to 5x)
    ↓
Final result with status
```

