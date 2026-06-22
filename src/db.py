import asyncpg
from pgvector.asyncpg import register_vector

from src.config import settings

_pool: asyncpg.Pool | None = None


def _parse_dsn(dsn: str) -> dict:
    """Parse DSN handling passwords that contain '@' characters."""
    import re
    # Match: scheme://user:password@host:port/dbname
    # Password is everything between first ':' after scheme and last '@' before host
    m = re.match(
        r"(?P<scheme>[^:]+)://(?P<user>[^:]+):(?P<password>.+)@(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<dbname>.+)",
        dsn,
    )
    if not m:
        return {"dsn": dsn}

    # Reconstruct with URL-encoded password to avoid ambiguity
    from urllib.parse import quote
    user = m.group("user")
    password = m.group("password")
    host = m.group("host")
    port = int(m.group("port") or 5432)
    dbname = m.group("dbname")

    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": dbname,
    }


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        conn_params = _parse_dsn(settings.supabase_url)
        conn_params.setdefault("ssl", "require")
        _pool = await asyncpg.create_pool(
            **conn_params,
            min_size=2,
            max_size=10,
            statement_cache_size=0,  # required for Supabase/PgBouncer transaction mode
            init=_init_connection,
        )
    return _pool


async def _init_connection(conn: asyncpg.Connection):
    await register_vector(conn)


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
