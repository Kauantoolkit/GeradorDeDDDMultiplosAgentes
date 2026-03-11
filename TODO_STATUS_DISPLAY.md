# TODO: Improve Frontend Status Display with Detailed Error Information

## Goal
Make the self-repair process more transparent by showing:
- Which specific errors were found
- Which services have the errors
- What fixes were attempted
- Which files were modified

## Changes Required

### 1. Backend: api/server.py
- [x] Update continue_generation to include detailed errors in WebSocket messages
- [x] Include service-specific error info
- [x] Include fix results with file names
- [x] **NEW**: Auto-create databases using psql command

### 2. Frontend: Timeline.jsx
- [x] Update to display detailed error info in event logs

### 3. Frontend: AgentCard.jsx
- [x] Update to display additional details from diagnostics

### 4. Frontend: index.css
- [x] Add CSS styles for detailed error display

### 5. New: infrastructure/database_creator.py
- [x] Create utility to automatically create PostgreSQL databases using psql

## Status: COMPLETED ✅

## What Was Changed

### Backend (api/server.py)
- Added detailed error extraction from validation results
- Now sends `detailed_errors` array with:
  - `type`: Error type (import_error, syntax_error, etc.)
  - `service`: Which service has the error
  - `message`: Full error message
  - `missing_dependency`: If applicable, what package to install
- Changed status message from vague "Corrigindo 11 erros" to detailed:
  - "11 erros encontrados em 2 serviço(s): clientes, pedidos. Primeiro erro: No module named 'email_validator'"
- **NEW**: Automatically creates databases when user clicks "Continue" using psql command

### New: infrastructure/database_creator.py
- Parses PostgreSQL URLs to extract host, port, user, password, database name
- Uses `psql` command to create databases automatically
- Falls back to manual creation if psql is not available

### Frontend (Timeline.jsx)
- Shows detailed errors in the event log panel
- Displays service name, error type, message, and missing dependencies

### Frontend (AgentCard.jsx)
- Shows detailed errors in the agent card diagnostics section
- Highlights missing dependencies in green

### CSS (index.css)
- Added styles for `.event-log-errors`, `.error-item`, `.error-service`, `.error-type`, `.error-msg`, `.error-dep`

## New Status Message Examples

Before:
```
Corrigindo 11 erros (tentativa 3/5)...
```

After:
```
11 erros encontrados em 2 serviço(s): clientes, pedidos. Primeiro erro: No module named 'email-validator'
```

## Database Auto-Creation

Now when user clicks "Continuar" button:
1. System checks if psql is available
2. If yes, automatically creates all databases using psql command
3. Shows progress: "Criando bancos de dados automaticamente..."
4. Shows result: "Bancos de dados criados automaticamente: clientes, pedidos, pagamentos"
5. If psql not found, falls back to manual instruction

