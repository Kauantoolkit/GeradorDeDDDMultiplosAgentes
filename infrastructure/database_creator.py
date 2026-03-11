"""
Database Creator - Cria bancos de dados PostgreSQL automaticamente
===============================================================

Este módulo fornece funções para criar bancos de dados PostgreSQL
automaticamente via linha de comando (psql), sem necessidade do pgAdmin.

Uso:
    from infrastructure.database_creator import create_databases
    
    database_urls = {
        "clientes": "postgresql://postgres:postgres@localhost:5432/clientes_db",
        "pedidos": "postgresql://postgres:postgres@localhost:5432/pedidos_db"
    }
    result = create_databases(database_urls)
"""

import subprocess
import re
import os
from urllib.parse import urlparse
from loguru import logger


def parse_postgresql_url(url: str) -> dict:
    """
    Parses a PostgreSQL URL into components.
    
    Args:
        url: PostgreSQL connection URL (e.g., postgresql://user:pass@host:5432/dbname)
        
    Returns:
        Dictionary with host, port, user, password, database
    """
    # Handle postgresql:// prefix
    if url.startswith("postgresql://"):
        url = url[12:]
    
    # Parse using urllib
    match = re.match(r'(?:(?P<user>[^:@]+)(?::(?P<password>[^@]+))?@)?(?P<host>[^:]+)(?::(?P<port>\d+))?/(?P<database>.*)', url)
    
    if match:
        return {
            "user": match.group("user") or "postgres",
            "password": match.group("password") or "",
            "host": match.group("host") or "localhost",
            "port": match.group("port") or "5432",
            "database": match.group("database") or "postgres"
        }
    
    # Default fallback
    return {
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": "5432",
        "database": "postgres"
    }


def create_database(
    host: str,
    port: str,
    user: str,
    password: str,
    database: str
) -> tuple[bool, str]:
    """
    Creates a PostgreSQL database using psql command.
    
    Args:
        host: PostgreSQL host
        port: PostgreSQL port
        user: PostgreSQL user
        password: PostgreSQL password
        database: Database name to create
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Set PGPASSWORD environment variable for authentication
        env = os.environ.copy()
        env["PGPASSWORD"] = password
        
        # First, connect to 'postgres' database to create the new database
        # Check if database already exists
        check_cmd = [
            "psql",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", "postgres",
            "-tAc",
            f"SELECT 1 FROM pg_database WHERE datname='{database}'"
        ]
        
        result = subprocess.run(
            check_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip() == "1":
            logger.info(f"Database '{database}' already exists, skipping creation")
            return True, f"Banco '{database}' já existe"
        
        # Create the database
        create_cmd = [
            "psql",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", "postgres",
            "-c",
            f"CREATE DATABASE {database}"
        ]
        
        result = subprocess.run(
            create_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully created database '{database}'")
            return True, f"Banco '{database}' criado com sucesso"
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            logger.error(f"Failed to create database '{database}': {error_msg}")
            return False, f"Erro ao criar banco '{database}': {error_msg}"
            
    except FileNotFoundError:
        return False, "psql não encontrado. Instale o PostgreSQL client"
    except subprocess.TimeoutExpired:
        return False, f"Timeout ao criar banco '{database}'"
    except Exception as e:
        return False, f"Erro ao criar banco '{database}': {str(e)}"


def create_databases(database_urls: dict) -> dict:
    """
    Creates multiple PostgreSQL databases from URLs.
    
    Args:
        database_urls: Dictionary mapping service names to PostgreSQL URLs
                      e.g., {"clientes": "postgresql://postgres:postgres@localhost:5432/clientes_db"}
        
    Returns:
        Dictionary with results: {
            "success": bool,
            "created": list of created database names,
            "failed": list of failed database names with errors,
            "messages": list of status messages
        }
    """
    results = {
        "success": True,
        "created": [],
        "failed": [],
        "messages": []
    }
    
    if not database_urls:
        results["messages"].append("Nenhuma URL de banco fornecida")
        return results
    
    logger.info(f"Creating {len(database_urls)} databases...")
    
    for service_name, url in database_urls.items():
        logger.info(f"Processing database for {service_name}: {url}")
        
        # Parse the URL
        parsed = parse_postgresql_url(url)
        
        logger.info(f"Parsed: host={parsed['host']}, port={parsed['port']}, user={parsed['user']}, database={parsed['database']}")
        
        # Create the database
        success, message = create_database(
            host=parsed["host"],
            port=parsed["port"],
            user=parsed["user"],
            password=parsed["password"],
            database=parsed["database"]
        )
        
        results["messages"].append(f"{service_name}: {message}")
        
        if success:
            results["created"].append(service_name)
        else:
            results["failed"].append(service_name)
            results["success"] = False
    
    # Summary
    logger.info(f"Database creation complete: {len(results['created'])} created, {len(results['failed'])} failed")
    
    return results


def check_psql_available() -> bool:
    """
    Check if psql command is available.
    
    Returns:
        True if psql is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    # Test
    print("Testing database creator...")
    
    if not check_psql_available():
        print("ERROR: psql not found. Please install PostgreSQL client.")
    else:
        print("psql is available")
        
        # Test with sample URLs
        test_urls = {
            "test_db": "postgresql://postgres:postgres@localhost:5432/test_db"
        }
        
        result = create_databases(test_urls)
        print(f"Result: {result}")

