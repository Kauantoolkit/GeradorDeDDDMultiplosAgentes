# TODO - Agent Corrections

## Task 1: Improve Executor Agent (executor_agent.py) ✅ COMPLETED
- [x] Generate more complete templates with related entities
- [x] Add more business logic methods to entities
- [x] Include DDD patterns (Domain Events, Domain Services)
- [x] Generate more complete use cases
- [x] Add entity relationships (Order -> OrderItem, Customer, Address)

## Task 2: Adjust Validator Agent (validator_agent.py) ✅ COMPLETED
- [x] Distinguish "empty file" from "basic template"
- [x] Be more flexible with DDD templates
- [x] Not expect production-ready code
- [x] Accept skeleton code as valid DDD structure

## Task 3: Improve Fix Agent (fix_agent.py) ✅ COMPLETED
- [x] NOT create empty __init__.py files (smart detection)
- [x] Complete existing basic templates automatically
- [x] Add entity-related methods when template is basic
- [x] Smart __init__.py creation (only if directory has other files)

## Task 4: Fix Requirements Generation ✅ COMPLETED
- [x] Auto-detect authentication requirement (via enhanced entity generation)
- [x] Generate auth-related entities when needed
- [x] Ensure all dependencies are generated
- [x] Enhanced entity generation with business methods

## Summary of Changes Made:

### Executor Agent (executor_agent.py):
1. Added `_generate_business_methods()` - generates entity-specific business logic methods
2. Added `_generate_entity_relationships()` - auto-generates related entities
3. Added `_detect_related_entities()` - detects related entities based on main entity
4. Enhanced entities with type-specific methods:
   - User: authenticate(), verify_email(), deactivate(), change_password()
   - Order: add_item(), remove_item(), calculate_total(), can_cancel(), cancel(), confirm(), complete()
   - Product: is_available(), decrease_stock(), increase_stock(), apply_discount()
   - Payment: process(), approve(), reject(), refund(), is_successful()

### Validator Agent (validator_agent.py):
1. Modified `_apply_guardrails()` to be more flexible:
   - No longer auto-rejects for minor issues
   - Distinguishes between critical issues and warnings
   - Only warns about placeholders/templates instead of failing
   - Reduces score but doesn't block for non-critical issues
   - Gives bonus score (0.8) for passing guardrails

### Fix Agent (fix_agent.py):
1. Added `_fix_init_files_smart()` - Smart __init__.py creation:
   - Only creates __init__.py if directory has other Python files
   - Replaces placeholder __init__.py with proper content
   - Generates proper module documentation based on layer (domain/application/infrastructure/api)

2. Added `_complete_basic_templates()` - Auto-complete basic templates:
   - Detects basic templates (entities without business logic)
   - Adds type-specific business methods automatically
   - Handles: User, Order, Product, Payment entities
   - Adds missing imports (datetime)

3. Added helper methods:
   - `_is_init_placeholder()` - Detects placeholder __init__.py
   - `_generate_proper_init()` - Generates proper __init__.py content by layer
   - `_is_basic_entity_template()` - Detects basic entity templates
   - `_extract_main_entity_name()` - Extracts entity name from content
   - `_complete_entity_template()` - Adds business methods to entities

### System Philosophy:
The system works as a team:
- **Executor**: Generates initial code (may be basic)
- **Validator**: Checks quality, distinguishes basic from empty
- **Fixer**: Completes and improves basic templates automatically
- **LLM-assisted Fix**: When available, uses AI for complex fixes

