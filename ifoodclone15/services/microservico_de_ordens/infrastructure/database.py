"""
Database Configuration - Infrastructure Layer
=============================================
Configuração de banco de dados (postgresql) - Async version.
"""

import asyncpg
import os
from typing import Optional


# Database connection pool
_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Obtém o pool de conexões do banco."""
    global _pool
    if _pool is None:
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:postgres@localhost:5432/dbname"
        )
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10
        )
    return _pool


async def close_db_pool():
    """Fecha o pool de conexões."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def init_db():
    """Inicializa o banco de dados criando as tabelas."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Create ordensentitys table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ordensentitys (
                id UUID PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)


def get_db():
    """Dependência para obter conexão do banco (async)."""
    return get_db_pool()
