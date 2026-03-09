"""Database configuration."""
import asyncpg
import os

_pool = None

async def get_db_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dbname")
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool

async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
