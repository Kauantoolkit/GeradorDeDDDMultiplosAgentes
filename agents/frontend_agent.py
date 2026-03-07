"""
Frontend Agent - Agente de Geração de Frontend Dinâmico
======================================================

Este agente é responsável por:
- Ler as rotas REST do backend gerado
- Gerar um frontend completo (React/Vue) que consome essas APIs
- Criar componentes CRUD dinâmicos baseados nas entidades
- Validar se o frontend funciona
"""

import json
import re
import os
from pathlib import Path
from typing import Any
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    Requirement
)
from infrastructure.llm_provider import OllamaProvider
from infrastructure.file_manager import FileManager


class FrontendAgent:
    """
    Agente para gerar frontend dinâmico baseado nas APIs do backend.
    """
    
    def __init__(self, llm_provider: OllamaProvider = None):
        self.llm_provider = llm_provider
        self.name = "Frontend Agent"
        logger.info(f"{self.name} inicializado")
    
    async def execute(
        self,
        project_path: str,
        requirement: Requirement = None
    ) -> ExecutionResult:
        """Executa a geração do frontend."""
        result = ExecutionResult(
            agent_type=AgentType.EXECUTOR,
            status=ExecutionStatus.IN_PROGRESS
        )
        
        try:
            logger.info("="*60)
            logger.info("FRONTEND AGENT - Iniciando geração")
            logger.info("="*60)
            
            file_manager = FileManager(project_path)
            
            # 1. Extrair rotas do backend
            routes = self._extract_routes_from_backend(project_path)
            logger.info(f"Rotas extraídas: {len(routes)}")
            for route in routes:
                logger.info(f"  - {route['method']} {route['path']}")
            
            # 2. Detectar entidades
            entities = self._detect_entities(project_path)
            logger.info(f"Entidades detectadas: {entities}")
            
            # 3. Gerar frontend React
            frontend_files = self._generate_react_app(project_path, routes, entities)
            
            # 4. Criar componentes
            components = self._generate_crud_components(project_path, routes, entities)
            
            # 5. Salvar arquivos
            created_files = []
            for file_path, content in {**frontend_files, **components}.items():
                if file_manager.create_file(file_path, content):
                    created_files.append(file_path)
            
            result.files_created = created_files
            result.status = ExecutionStatus.SUCCESS
            result.output = f"Frontend gerado com {len(created_files)} arquivos"
            
            logger.info(f"Frontend gerado: {len(created_files)} arquivos")
            
            return result
            
        except Exception as e:
            logger.exception(f"Erro no {self.name}: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            return result
    
    def _extract_routes_from_backend(self, project_path: str) -> list[dict]:
        """Extrai as rotas REST do backend."""
        routes = []
        services_path = Path(project_path) / "services"
        
        if not services_path.exists():
            return routes
        
        for service_dir in services_path.iterdir():
            if not service_dir.is_dir():
                continue
            
            routes_file = service_dir / "api" / "routes.py"
            if not routes_file.exists():
                continue
            
            try:
                with open(routes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                route_pattern = r'@router\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']'
                matches = re.findall(route_pattern, content)
                
                for method, path in matches:
                    entity = self._extract_entity_from_path(path)
                    routes.append({
                        "method": method.upper(),
                        "path": path,
                        "entity": entity,
                        "service": service_dir.name
                    })
                    
            except Exception as e:
                logger.warning(f"Erro ao ler rotas de {service_dir.name}: {e}")
        
        return routes
    
    def _extract_entity_from_path(self, path: str) -> str:
        """Extrai o nome da entidade a partir do path."""
        path = path.replace("/api/", "")
        segments = path.split("/")
        if segments:
            entity = segments[0]
            if entity.endswith("s"):
                entity = entity[:-1]
            entity = "".join(word.capitalize() for word in entity.split("_"))
            return entity
        return "Entity"
    
    def _detect_entities(self, project_path: str) -> list[str]:
        """Detecta as entidades do projeto."""
        entities = set()
        services_path = Path(project_path) / "services"
        
        if not services_path.exists():
            return list(entities)
        
        for service_dir in services_path.iterdir():
            if not service_dir.is_dir():
                continue
            
            domain_dir = service_dir / "domain"
            if not domain_dir.exists():
                continue
            
            for entity_file in domain_dir.glob("*entities.py"):
                try:
                    with open(entity_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    class_pattern = r'class\s+(\w+)\s*[:\(]'
                    matches = re.findall(class_pattern, content)
                    
                    for match in matches:
                        if not match.startswith('_'):
                            entities.add(match)
                            
                except Exception as e:
                    logger.warning(f"Erro ao ler entidades de {entity_file}: {e}")
        
        return list(entities)
    
    def _generate_react_app(self, project_path: str, routes: list, entities: list) -> dict:
        """Gera a estrutura base de um projeto React."""
        files = {}
        project_name = Path(project_path).name
        
        files["frontend/package.json"] = self._generate_package_json(project_name)
        files["frontend/vite.config.js"] = self._generate_vite_config()
        files["frontend/index.html"] = self._generate_index_html(project_name)
        files["frontend/src/main.jsx"] = self._generate_main_jsx()
        files["frontend/src/App.jsx"] = self._generate_app_jsx(entities)
        files["frontend/src/services/api.js"] = self._generate_api_service(routes)
        
        return files
    
    def _generate_package_json(self, project_name: str) -> str:
        return """{
  "name": "PROJECTNAME-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
""".replace("PROJECTNAME", project_name)
    
    def _generate_vite_config(self) -> str:
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
"""
    
    def _generate_index_html(self, project_name: str) -> str:
        title = project_name.title()
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} - Sistema de Gestão</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
    
    def _generate_main_jsx(self) -> str:
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    def _generate_app_jsx(self, entities: list) -> str:
        # Build nav items
        nav_lines = []
        for entity in entities:
            nav_lines.append(f"            <li><Link to=\"/{entity.lower()}s\">{entity}s</Link></li>")
        nav_items = "\n".join(nav_lines)
        
        # Build route lines
        route_lines = []
        for entity in entities:
            route_lines.append(f'            <Route path="/{entity.lower()}s" element=<{entity}List /> />')
        routes_str = "\n".join(route_lines)
        
        # Build imports
        import_lines = []
        for entity in entities:
            import_lines.append(f"import {entity}List from './components/{entity}List';")
        imports = "\n".join(import_lines)
        
        return f"""import React from 'react';
import {{ BrowserRouter, Routes, Route, Link }} from 'react-router-dom';
import ApiService from './services/api';
{imports}

function Home() {{
  return (
    <div className="home">
      <h1>Bem-vindo ao Sistema</h1>
      <p>Selecione uma opção no menu acima</p>
    </div>
  );
}}

function App() {{
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="sidebar">
          <h2>Menu</h2>
          <ul>
            <li><Link to="/">Home</Link></li>
{nav_items}
          </ul>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element=<Home /> />
{routes_str}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}}

export default App;
"""
    
    def _generate_api_service(self, routes: list) -> str:
        method_lines = []
        
        for route in routes:
            entity = route.get("entity", "Entity")
            method = route.get("method", "GET")
            path = route.get("path", "")
            
            if method == "GET" and "{" not in path:
                method_lines.append(f"""  async get{entity}s() {{
    const response = await axios.get('{path}');
    return response.data;
  }}""")
            
            elif method == "GET" and "{" in path:
                method_lines.append(f"""  async get{entity}(id) {{
    const response = await axios.get('{path}'.replace('${{'id'}}', id));
    return response.data;
  }}""")
            
            elif method == "POST":
                method_lines.append(f"""  async create{entity}(data) {{
    const response = await axios.post('{path}', data);
    return response.data;
  }}""")
            
            elif method == "PUT":
                method_lines.append(f"""  async update{entity}(id, data) {{
    const response = await axios.put('{path}'.replace('${{'id'}}', id), data);
    return response.data;
  }}""")
            
            elif method == "DELETE":
                method_lines.append(f"""  async delete{entity}(id) {{
    const response = await axios.delete('{path}'.replace('${{'id'}}', id));
    return response.data;
  }}""")
        
        methods = "\n".join(method_lines)
        
        return f"""import axios from 'axios';

const ApiService = axios.create({{
  baseURL: '/api',
  timeout: 10000,
  headers: {{
    'Content-Type': 'application/json'
  }}
}});

export default {{{methods}
}};
"""
    
    def _generate_crud_components(self, project_path: str, routes: list, entities: list) -> dict:
        """Gera componentes CRUD para cada entidade."""
        components = {}
        
        for entity in entities:
            entity_routes = [r for r in routes if r.get("entity") == entity]
            components[f"frontend/src/components/{entity}List.jsx"] = self._generate_crud_component(entity, entity_routes)
        
        components["frontend/src/index.css"] = self._generate_css()
        
        return components
    
    def _generate_crud_component(self, entity: str, routes: list) -> str:
        # Using regular string to avoid f-string issues with JSX braces
        entity_lower = entity.lower()
        return """import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';

function ENTITYList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    loadItems();
  }, []);
  
  async function loadItems() {
    try {
      setLoading(true);
      const data = await ApiService.getENTITYs();
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  
  async function handleDelete(id) {
    if (!confirm('Tem certeza que deseja excluir?')) return;
    try {
      await ApiService.deleteENTITY(id);
      setItems(items.filter(item => item.id !== id));
    } catch (err) {
      alert('Erro ao excluir: ' + err.message);
    }
  }
  
  if (loading) return <div className="loading">Carregando...</div>;
  if (error) return <div className="error">Erro: {error}</div>;
  
  return (
    <div className="crud-container">
      <h1>ENTITYs</h1>
      
      <table className="crud-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.nome || item.name || 'N/A'}</td>
              <td>
                <button onClick={() => handleDelete(item.id)} className="btn-delete">
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {items.length === 0 && (
        <p className="empty">Nenhum ENTITY_lower encontrado</p>
      )}
    </div>
  );
}

export default ENTITYList;
""".replace("ENTITY", entity).replace("ENTITY_lower", entity_lower)
    
    def _generate_css(self) -> str:
        return """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Poppins', sans-serif;
}

:root {
  --primary: #ff6b35;
  --secondary: #004e89;
  --dark: #1a1a2e;
  --light: #f7f7f7;
  --gray: #666;
}

body {
  background: var(--light);
}

.app {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 250px;
  background: white;
  padding: 20px;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.sidebar h2 {
  color: var(--primary);
  margin-bottom: 20px;
}

.sidebar ul {
  list-style: none;
}

.sidebar li {
  margin-bottom: 10px;
}

.sidebar a {
  display: block;
  padding: 12px;
  color: var(--gray);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s;
}

.sidebar a:hover {
  background: var(--primary);
  color: white;
}

.content {
  flex: 1;
  padding: 30px;
}

.crud-container {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.crud-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.crud-table th,
.crud-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.crud-table th {
  background: var(--dark);
  color: white;
}

.btn-delete {
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
}

.btn-delete:hover {
  background: #c82333;
}

.loading, .error, .empty {
  text-align: center;
  padding: 40px;
  color: var(--gray);
}

.error {
  color: #dc3545;
}
"""


async def generate_frontend(project_path: str, llm_provider=None) -> ExecutionResult:
    """Gera frontend para o projeto."""
    agent = FrontendAgent(llm_provider)
    return await agent.execute(project_path)

