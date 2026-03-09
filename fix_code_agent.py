#!/usr/bin/env python3
"""Fix code_agent.py generation issues."""

import re

with open('agents/code_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Application Layer __init__
old_app = 'files[f"{base_path}/application/__init__.py"] = f"Application Layer - {service_name}\\n"'
new_app = '''files[f"{base_path}/application/__init__.py"] = \'\'\'"""Application Layer - {service_name}."""
from .dtos import *
from .mappers import *
from .use_cases import *
\'\'\'
'''
content = content.replace(old_app, new_app)

# Fix Infrastructure Layer __init__
old_infra = 'files[f"{base_path}/infrastructure/__init__.py"] = "Infrastructure Layer\\n"'
new_infra = '''files[f"{base_path}/infrastructure/__init__.py"] = \'\'\'"""Infrastructure Layer."""
from .repositories import *
from .database import *
\'\'\'
'''
content = content.replace(old_infra, new_infra)

# Fix API Layer __init__
old_api = 'files[f"{base_path}/api/__init__.py"] = "API Layer\\n"'
new_api = '''files[f"{base_path}/api/__init__.py"] = \'\'\'"""API Layer."""
from .routes import router
from .schemas import *
\'\'\'
'''
content = content.replace(old_api, new_api)

# Fix main.py to use relative imports
old_main = 'from api.routes import router'
new_main = 'from .api.routes import router'
content = content.replace(old_main, new_main)

# Fix routes.py to import get_repository function - needs entity_lower variable
# This is trickier because it's in an f-string
old_routes_template = 'from infrastructure.repositories import {entity}RepositoryImpl'
# We need to fix the _generate_routes method instead

with open('agents/code_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Step 1 done - __init__ files and main.py imports fixed')

# Now fix the _generate_routes method
with open('agents/code_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix _generate_routes method
old_routes_import = '''from infrastructure.repositories import {entity}RepositoryImpl

router = APIRouter(prefix="/api/{service_name}", tags=["{service_name}"])'''

new_routes_import = '''from infrastructure.repositories import {entity}RepositoryImpl, get_{entity_lower}_repository

router = APIRouter(prefix="/api/{service_name}", tags=["{service_name}"])'''

content = content.replace(old_routes_import, new_routes_import)

with open('agents/code_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Step 2 done - routes.py imports fixed')
print('All fixes applied successfully!')

