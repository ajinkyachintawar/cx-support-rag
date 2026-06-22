import re
import asyncpg

_POLICY_CODE_RE = re.compile(r"[A-Z]{2,}-[A-Z0-9][\w-]*")


def extract_policy_codes(query: str) -> list[str]:
    return _POLICY_CODE_RE.findall(query.upper())


async def keyword_search(
    query: str,
    pool: asyncpg.Pool,
    top_k: int = 10,
) -> list[dict]:
    policy_codes = extract_policy_codes(query)

    async with pool.acquire() as conn:
        ts_rows = await conn.fetch(
            """
            SELECT id, source, content,
                   ts_rank(ts_content, plainto_tsquery('english', $1)) AS score
            FROM documents
            WHERE ts_content @@ plainto_tsquery('english', $1)
            ORDER BY score DESC
            LIMIT $2
            """,
            query,
            top_k,
        )
        ts_results = [dict(r) for r in ts_rows]

        if policy_codes:
            pattern = "|".join(re.escape(code) for code in policy_codes)
            code_rows = await conn.fetch(
                """
                SELECT id, source, content, 1.0::float AS score
                FROM documents
                WHERE content ~* $1
                LIMIT $2
                """,
                pattern,
                top_k,
            )
            seen_ids = {r["id"] for r in ts_results}
            for row in code_rows:
                if row["id"] not in seen_ids:
                    ts_results.append(dict(row))
                    seen_ids.add(row["id"])

    return ts_results[:top_k]
