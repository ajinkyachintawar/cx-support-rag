import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db import get_pool, close_pool
from src.ingestion.pipeline import run_ingestion


async def main():
    pool = await get_pool()
    try:
        count = await run_ingestion(pool)
        print(f"Ingestion complete: {count} chunks in database")
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
