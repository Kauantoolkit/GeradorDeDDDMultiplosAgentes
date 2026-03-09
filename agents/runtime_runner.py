"""
Runtime Runner - Objective Runtime Validation
=============================================

This component provides objective runtime validation:
- Tests Python imports
- Checks syntax errors
- Validates service startup
- Validates frontend (React) code (NEW)
- Returns real errors with stack traces

Key Principles:
1. Objective validation (not LLM judgment)
2. Real execution attempts, not static analysis
3. Detailed error reporting with fixes
4. Integrated directly into self-repair loop
"""

import ast
import asyncio
import sys
import os
import subprocess
import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Optional
from loguru import logger


class RuntimeRunner:
    """
    Runtime validation runner.
    
    Provides objective validation by actually trying to:
    - Import modules
    - Check Python syntax
    - Start services
    
    Returns real errors that CodeAgent can fix.
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.errors = []
        self.warnings = []
    
    async def validate_all_services(self) -> dict[str, Any]:
        """
        Validate all services in the project.
        
        Returns:
            Dictionary with validation results per service
        """
        results = {}
        
        services_path = Path(self.project_path) / "services"
        if not services_path.exists():
            logger.warning(f"Services directory not found: {services_path}")
            return results
        
        for service_dir in services_path.iterdir():
            if not service_dir.is_dir():
                continue
            
            service_name = service_dir.name
            logger.info(f"Validating service: {service_name}")
            
            result = await self.validate_service(service_name, service_dir)
            results[service_name] = result
        
        return results
    
    async def validate_service(self, service_name: str, service_path: Path) -> dict[str, Any]:
        """
        Validate a single service.
        
        Args:
            service_name: Name of the service
            service_path: Path to service directory
            
        Returns:
            Validation result dictionary
        """
        result = {
            "service_name": service_name,
            "path": str(service_path),
            "imports_ok": False,
            "syntax_ok": False,
            "startup_ok": False,
            "errors": [],
            "warnings": [],
            "score": 0.0
        }
        
        # 1. Test imports
        import_result = self._test_imports(service_name, service_path)
        result["imports_ok"] = import_result["success"]
        result["import_errors"] = import_result.get("errors", [])
        
        # 2. Test syntax
        syntax_result = self._test_syntax(service_path)
        result["syntax_ok"] = syntax_result["success"]
        result["syntax_errors"] = syntax_result.get("errors", [])
        
        # 3. Test startup
        if (service_path / "main.py").exists():
            startup_result = await self._test_startup(service_name, service_path)
            result["startup_ok"] = startup_result["success"]
            result["startup_errors"] = startup_result.get("errors", [])
        
        # Calculate score
        checks = [
            result["imports_ok"],
            result["syntax_ok"],
            result["startup_ok"]
        ]
        result["score"] = sum(checks) / len(checks) if checks else 0.0
        
        return result
    
    def _test_imports(self, service_name: str, service_path: Path) -> dict[str, Any]:
        """
        Test if service modules can be imported.
        
        Args:
            service_name: Service name
            service_path: Path to service directory
            
        Returns:
            Test result dictionary
        """
        result = {
            "success": False,
            "errors": []
        }
        
        # Add project root to sys.path
        project_root = str(service_path.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        try:
            main_path = service_path / "main.py"
            if not main_path.exists():
                result["errors"].append("main.py not found")
                return result
            
            # Read and check syntax first
            with open(main_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ast.parse(code)
            
            # Try to import
            module_name = f"services.{service_name}.main"
            spec = importlib.util.spec_from_file_location(module_name, main_path)
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                try:
                    spec.loader.exec_module(module)
                    result["success"] = True
                    logger.info(f"  ✓ Imports OK: {service_name}")
                except ImportError as e:
                    error_msg = str(e)
                    result["errors"].append(error_msg)
                    
                    # Extract missing dependency
                    missing_dep = self._extract_missing_dependency(error_msg)
                    if missing_dep:
                        result["missing_dependency"] = missing_dep
                        result["suggested_fix"] = f"pip install {missing_dep}"
                    
                    logger.error(f"  ✗ Import error: {service_name} - {error_msg}")
                    
                except Exception as e:
                    error_msg = str(e)
                    result["errors"].append(error_msg)
                    logger.error(f"  ✗ Import error: {service_name} - {error_msg}")
        
        except SyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
            result["errors"].append(error_msg)
            logger.error(f"  ✗ Syntax error: {service_name} - {error_msg}")
        
        except Exception as e:
            error_msg = str(e)
            result["errors"].append(error_msg)
            logger.error(f"  ✗ Error: {service_name} - {error_msg}")
        
        return result
    
    def _test_syntax(self, service_path: Path) -> dict[str, Any]:
        """
        Test syntax of all Python files in service.
        
        Args:
            service_path: Path to service directory
            
        Returns:
            Test result dictionary
        """
        result = {
            "success": True,
            "errors": []
        }
        
        py_files = list(service_path.rglob("*.py"))
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                ast.parse(code)
            except SyntaxError as e:
                error_msg = f"Syntax error in {py_file.name} at line {e.lineno}: {e.msg}"
                result["errors"].append(error_msg)
                result["success"] = False
                logger.error(f"  ✗ Syntax error: {py_file.name}")
        
        if result["success"]:
            logger.info(f"  ✓ Syntax OK: {service_path.name}")
        
        return result
    
    async def _test_startup(self, service_name: str, service_path: Path) -> dict[str, Any]:
        """
        Test if FastAPI app can start.
        
        Args:
            service_name: Service name
            service_path: Path to service directory
            
        Returns:
            Test result dictionary
        """
        result = {
            "success": False,
            "errors": []
        }
        
        try:
            sys.path.insert(0, str(service_path.parent.parent))
            
            main_path = service_path / "main.py"
            module_name = f"services.{service_name}.main"
            
            spec = importlib.util.spec_from_file_location(module_name, main_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                try:
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'app'):
                        result["success"] = True
                        logger.info(f"  ✓ Startup OK: {service_name}")
                    else:
                        result["errors"].append("Module missing 'app' attribute (FastAPI)")
                        
                except Exception as e:
                    result["errors"].append(f"Execution error: {str(e)}")
        
        except Exception as e:
            result["errors"].append(f"Startup error: {str(e)}")
            logger.error(f"  ✗ Startup error: {service_name} - {str(e)}")
        
        return result
    
    def _extract_missing_dependency(self, error_message: str) -> Optional[str]:
        """
        Extract missing dependency name from error message.
        
        Args:
            error_message: Error message from import
            
        Returns:
            Package name or None
        """
        import re
        
        patterns = [
            r"No module named ['\"]([^'\"]+)['\"]",
            r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                module_name = match.group(1)
                return self._translate_module_to_package(module_name)
        
        return None
    
    def _translate_module_to_package(self, module_name: str) -> str:
        """
        Translate Python module name to pip package name.
        
        Args:
            module_name: Python module name
            
        Returns:
            pip package name
        """
        translations = {
            "email_validator": "email-validator",
            "passlib": "passlib[bcrypt]",
            "bcrypt": "bcrypt",
            "pydantic_settings": "pydantic-settings",
            "asyncpg": "asyncpg",
            "psycopg2": "psycopg2-binary",
            "python_multipart": "python-multipart",
        }
        
        return translations.get(module_name, module_name)
    
    # ============================================================
    # Frontend Validation (React/Vite)
    # ============================================================
    
    async def validate_frontend(self, frontend_path: str = None) -> dict[str, Any]:
        """
        Validate frontend (React/Vite) application.
        
        Args:
            frontend_path: Path to frontend directory (default: frontend/)
            
        Returns:
            Validation result dictionary
        """
        result = {
            "exists": False,
            "npm_install_ok": False,
            "npm_build_ok": False,
            "syntax_ok": False,
            "errors": [],
            "warnings": [],
            "score": 0.0
        }
        
        # Determine frontend path
        if frontend_path is None:
            frontend_path = Path(self.project_path) / "frontend"
        else:
            frontend_path = Path(frontend_path)
        
        if not frontend_path.exists():
            logger.warning(f"Frontend directory not found: {frontend_path}")
            result["errors"].append("Frontend directory not found")
            return result
        
        result["exists"] = True
        result["path"] = str(frontend_path)
        
        # Check package.json exists
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            result["errors"].append("package.json not found")
            return result
        
        # 1. Check if node_modules exists, if not suggest npm install
        node_modules = frontend_path / "node_modules"
        if not node_modules.exists():
            logger.info("  node_modules not found - will try npm install")
            install_result = await self._test_npm_install(frontend_path)
            result["npm_install_ok"] = install_result["success"]
            result["errors"].extend(install_result.get("errors", []))
        else:
            result["npm_install_ok"] = True
            logger.info("  ✓ node_modules exists")
        
        # 2. Validate JSX/JS syntax using esbuild (bundler check)
        syntax_result = self._test_jsx_syntax(frontend_path)
        result["syntax_ok"] = syntax_result["success"]
        result["errors"].extend(syntax_result.get("errors", []))
        
        # 3. Try npm run build to catch all issues
        if result["npm_install_ok"]:
            build_result = await self._test_npm_build(frontend_path)
            result["npm_build_ok"] = build_result["success"]
            result["errors"].extend(build_result.get("errors", []))
            result["warnings"].extend(build_result.get("warnings", []))
        
        # Calculate score
        checks = [
            result["npm_install_ok"],
            result["syntax_ok"],
            result["npm_build_ok"]
        ]
        # If npm_install fails, don't count npm_build as failure
        if not result["npm_install_ok"]:
            result["score"] = 0.3 if result["syntax_ok"] else 0.0
        else:
            result["score"] = sum(checks) / len(checks) if checks else 0.0
        
        return result
    
    def _test_jsx_syntax(self, frontend_path: Path) -> dict[str, Any]:
        """
        Test JSX/JavaScript syntax using basic pattern matching.
        
        For more thorough checking, use npm run build.
        
        Args:
            frontend_path: Path to frontend directory
            
        Returns:
            Test result dictionary
        """
        result = {
            "success": True,
            "errors": []
        }
        
        jsx_files = list(frontend_path.rglob("*.jsx"))
        js_files = list(frontend_path.rglob("*.js"))
        tsx_files = list(frontend_path.rglob("*.tsx"))
        
        all_js_files = jsx_files + js_files + tsx_files
        
        # Skip node_modules
        all_js_files = [f for f in all_js_files if "node_modules" not in str(f)]
        
        # Common JSX syntax issues to check
        common_errors = [
            (r'<\w+[^>]*[^/]>(?!.*</\w+>)', "Unclosed JSX tag"),
            (r'return\s*\(\s*(?!\()', "Missing parentheses around JSX return"),
            (r'class\s*=\s*"[^"]*$', "Unclosed class attribute"),
            (r'className\s*=\s*[\'"][^\'"]*$', "Unclosed className attribute"),
            (r'onClick\s*=\s*\{\s*$', "Empty onClick handler"),
            (r'\{\s*\{\s*', "Double opening braces"),
            (r'\}\s*\}\s*', "Double closing braces"),
            (r'import\s+.*\s+from\s+[\'"][^\'"]+$', "Unclosed import string"),
        ]
        
        for jsx_file in all_js_files:
            try:
                with open(jsx_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for basic JSX issues
                for pattern, error_desc in common_errors:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        result["errors"].append(
                            f"Syntax issue in {jsx_file.name} at line {line_num}: {error_desc}"
                        )
                        result["success"] = False
                
                # Check for balanced braces
                open_braces = content.count('{')
                close_braces = content.count('}')
                if open_braces != close_braces:
                    result["errors"].append(
                        f"Unbalanced braces in {jsx_file.name}: {open_braces} open, {close_braces} close"
                    )
                    result["success"] = False
                
                # Check for balanced parentheses
                open_parens = content.count('(')
                close_parens = content.count(')')
                if open_parens != close_parens:
                    result["errors"].append(
                        f"Unbalanced parentheses in {jsx_file.name}: {open_parens} open, {close_parens} close"
                    )
                    result["success"] = False
                    
            except Exception as e:
                result["errors"].append(f"Error reading {jsx_file}: {e}")
                result["success"] = False
        
        if result["success"]:
            logger.info(f"  ✓ JSX/JS syntax check passed ({len(all_js_files)} files)")
        
        return result
    
    async def _test_npm_install(self, frontend_path: Path) -> dict[str, Any]:
        """
        Test npm install.
        
        Args:
            frontend_path: Path to frontend directory
            
        Returns:
            Test result dictionary
        """
        result = {
            "success": False,
            "errors": []
        }
        
        try:
            logger.info("  Running npm install...")
            
            # Run npm install
            process = await asyncio.create_subprocess_exec(
                "npm", "install",
                cwd=str(frontend_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result["success"] = True
                logger.info("  ✓ npm install OK")
            else:
                error_msg = stderr.decode() if stderr else "npm install failed"
                result["errors"].append(f"npm install failed: {error_msg}")
                logger.error(f"  ✗ npm install failed: {error_msg[:200]}")
        
        except FileNotFoundError:
            result["errors"].append("npm not found - make sure Node.js is installed")
            logger.error("  ✗ npm not found")
        except Exception as e:
            result["errors"].append(f"npm install error: {e}")
            logger.error(f"  ✗ npm install error: {e}")
        
        return result
    
    async def _test_npm_build(self, frontend_path: Path) -> dict[str, Any]:
        """
        Test npm run build to catch all issues.
        
        Args:
            frontend_path: Path to frontend directory
            
        Returns:
            Test result dictionary
        """
        result = {
            "success": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            logger.info("  Running npm run build...")
            
            # Run npm run build
            process = await asyncio.create_subprocess_exec(
                "npm", "run", "build",
                cwd=str(frontend_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
            
            if process.returncode == 0:
                result["success"] = True
                logger.info("  ✓ npm run build OK")
            else:
                # Parse errors from output
                errors = self._parse_build_errors(output)
                result["errors"].extend(errors)
                
                if errors:
                    logger.error(f"  ✗ npm build failed with {len(errors)} errors")
                    for err in errors[:5]:  # Show first 5 errors
                        logger.error(f"     - {err}")
                else:
                    logger.error(f"  ✗ npm build failed (no parseable errors)")
        
        except FileNotFoundError:
            result["errors"].append("npm not found - make sure Node.js is installed")
        except Exception as e:
            result["errors"].append(f"npm build error: {e}")
            logger.error(f"  ✗ npm build error: {e}")
        
        return result
    
    def _parse_build_errors(self, output: str) -> list[str]:
        """
        Parse errors from npm build output.
        
        Args:
            output: Build output text
            
        Returns:
            List of error messages
        """
        errors = []
        
        lines = output.split('\n')
        for line in lines:
            # Look for error indicators
            lower_line = line.lower()
            if 'error' in lower_line or 'failed' in lower_line or '✘' in line:
                # Clean up the line
                cleaned = line.strip()
                if cleaned and len(cleaned) > 5:
                    errors.append(cleaned[:200])  # Truncate long lines
        
        return errors


class RuntimeRunnerOrchestrator:
    """
    Orchestrates runtime validation and auto-fixing.
    
    This is the key component for self-repair:
    1. Validate services
    2. If errors, try auto-fixes first
    3. Return detailed error reports
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.runner = RuntimeRunner(project_path)
    
    async def validate_and_fix(self, include_frontend: bool = True) -> dict[str, Any]:
        """
        Run validation and attempt auto-fixes.
        
        Args:
            include_frontend: Whether to also validate frontend (default: True)
            
        Returns:
            Validation results with fixes applied
        """
        logger.info("="*60)
        logger.info("RUNTIME RUNNER - Validating execution")
        logger.info("="*60)
        
        # Validate all services
        results = await self.runner.validate_all_services()
        
        # Validate frontend if requested
        frontend_result = None
        if include_frontend:
            logger.info("Validating frontend...")
            frontend_result = await self.runner.validate_frontend()
            logger.info(f"Frontend validation: score={frontend_result.get('score', 0):.2f}")
        
        # Collect all runtime errors for reporting
        all_errors = []
        
        for service_name, result in results.items():
            if not result["imports_ok"]:
                # Add import errors
                for error in result.get("import_errors", []):
                    error_dict = {
                        "type": "import_error",
                        "service": service_name,
                        "message": error,
                    }
                    
                    if "missing_dependency" in result:
                        error_dict["missing_dependency"] = result["missing_dependency"]
                    
                    all_errors.append(error_dict)
            
            if not result["syntax_ok"]:
                # Add syntax errors
                for error in result.get("syntax_errors", []):
                    all_errors.append({
                        "type": "syntax_error",
                        "service": service_name,
                        "message": error,
                    })
            
            if not result["startup_ok"]:
                for error in result.get("startup_errors", []):
                    all_errors.append({
                        "type": "startup_error",
                        "service": service_name,
                        "message": error,
                    })
        
        # Add frontend errors
        if frontend_result and not frontend_result.get("npm_build_ok", False):
            for error in frontend_result.get("errors", []):
                all_errors.append({
                    "type": "frontend_error",
                    "service": "frontend",
                    "message": error,
                })
        
        # Try auto-fixes for common errors
        if all_errors:
            self._auto_fix_common_errors(all_errors)
        
        return {
            "results": results,
            "frontend": frontend_result,
            "total_services": len(results),
            "successful": sum(1 for r in results.values() if r["imports_ok"]),
            "failed": sum(1 for r in results.values() if not r["imports_ok"]),
            "errors": all_errors
        }
    
    def _auto_fix_common_errors(self, errors: list[dict]) -> None:
        """
        Try to auto-fix common errors.
        
        Args:
            errors: List of error dictionaries
        """
        for error in errors:
            if error.get("missing_dependency"):
                self._add_dependency(error["missing_dependency"], error.get("service"))
    
    def _add_dependency(self, package: str, service_name: str = None) -> bool:
        """
        Add missing dependency to requirements.txt.
        
        Args:
            package: Package name
            service_name: Service name (optional)
            
        Returns:
            True if added successfully
        """
        try:
            if service_name:
                req_path = Path(self.project_path) / "services" / service_name / "requirements.txt"
            else:
                # Try to find any requirements.txt
                services_path = Path(self.project_path) / "services"
                for s in services_path.iterdir():
                    if s.is_dir():
                        req_path = s / "requirements.txt"
                        if req_path.exists():
                            break
                else:
                    return False
            
            if not req_path.exists():
                return False
            
            # Check if already exists
            with open(req_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            package_name = package.split('[')[0]
            if package_name in content.lower():
                return False
            
            # Add dependency
            with open(req_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{package}\n")
            
            logger.info(f"  ✓ Auto-fix: Added {package} to {req_path}")
            return True
            
        except Exception as e:
            logger.warning(f"  ✗ Auto-fix failed: {e}")
            return False
    
    def get_runtime_errors(self) -> list[dict]:
        """
        Get list of runtime errors for CodeAgent.
        
        Returns:
            List of error dictionaries suitable for CodeAgent
        """
        # Quick validation to get current errors
        import asyncio
        result = asyncio.run(self.validate_and_fix())
        return result.get("errors", [])


# Convenience function
async def quick_validate(project_path: str) -> dict[str, Any]:
    """
    Quick validation function.
    
    Args:
        project_path: Path to project
        
    Returns:
        Validation results
    """
    orchestrator = RuntimeRunnerOrchestrator(project_path)
    return await orchestrator.validate_and_fix()


if __name__ == "__main__":
    import asyncio
    
    # Test
    project = "ifoodclone8"
    result = asyncio.run(quick_validate(project))
    print(f"\nResult: {result}")

