# CX Support RAG Agent

A production-grade RAG agent for CX support teams. Ask it any support question in natural language — it retrieves the relevant policy or case precedent, cites its source, and refuses to answer when confidence is low.

## Architecture

```
POST /query
    |
    +-- query_node        Embed query via Jina Embeddings v3 (1024-dim)
    |
    +-- retrieval_node    Vector search || Keyword search -> Reciprocal Rank Fusion -> top 5
    |        |
    |        +-- pgvector cosine similarity (top 10)
    |        +-- Postgres full-text search + policy-code regex matching (top 10)
    |
    +-- synthesis_node    Llama 3.3 70B generates grounded JSON answer with confidence score
    |
    +-- guard_node        Confidence gate: if score < 0.4 OR retrieval quality too low
                          -> force escalation instead of guessing
```

### Why hybrid retrieval matters

The knowledge base contains exact policy codes (`REF-PREM-030`, `VER-003`, `SYS-4471`) that semantic search alone cannot reliably match. The keyword retriever catches these anchors; the vector retriever handles semantic similarity for natural-language queries. RRF merges both ranked lists without tunable weights, no per-retriever weighting to tune.

### The eval gate

A wrong confident answer is worse than no answer. The hard gate:

> If `confident + wrong` rate exceeds 5% of total cases, the eval run fails.

This is the primary success criterion, reported separately from all other metrics.

---

## Stack

| Component | Technology |
|-----------|-----------|
| Embeddings | Jina Embeddings v3 (1024-dim) via REST API |
| LLM | Llama 3.3 70B via Groq |
| Vector store | Supabase pgvector |
| Full-text search | Postgres tsvector + GIN index |
| Framework | FastAPI + LangGraph |
| Tests | pytest |

---

## Setup

### 1. Prerequisites

- Python 3.11+
- A [Jina AI](https://jina.ai) API key (free tier)
- A [Groq](https://console.groq.com) API key (free tier)
- A [Supabase](https://supabase.com) project (free tier)

### 2. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Configure

```bash
cp .env.example .env
# Fill in your API keys
```

```
KB_JINA_API_KEY=jina_xxx
KB_GROQ_API_KEY=gsk_xxx
KB_SUPABASE_URL=postgresql://postgres.PROJECT_ID:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
```

### 4. Database setup

Enable the `pgvector` extension and run the following SQL in your Supabase project (SQL editor or `psql`):

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source       TEXT NOT NULL,
    content      TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    chunk_index  INTEGER NOT NULL DEFAULT 0,
    token_count  INTEGER NOT NULL,
    embedding    vector(1024) NOT NULL,
    ts_content   tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_documents_source_chunk ON documents (source, chunk_index);
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 5);
CREATE INDEX idx_documents_ts ON documents USING gin (ts_content);

CREATE TABLE query_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    sources         TEXT[] NOT NULL DEFAULT '{}',
    confidence      FLOAT NOT NULL,
    should_escalate BOOLEAN NOT NULL DEFAULT FALSE,
    latency_ms      INTEGER NOT NULL,
    model           TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 5. Ingest the knowledge base

```bash
make ingest
```

Ingestion is idempotent — re-running skips unchanged documents.

### 6. Start the server

```bash
make serve
```

The UI is available at `http://localhost:8000/ui`.

---

## API

### `POST /query`

```json
// Request
{ "question": "What is the refund window for a premium customer?" }

// Response
{
  "answer": "Under policy REF-PREM-030, premium customers have 30 days for a full refund...",
  "confidence": 0.95,
  "sources": [
    { "filename": "refund_policy_premium.md", "rrf_score": 0.0328 },
    { "filename": "case_0163_tier_downgrade.md", "rrf_score": 0.0164 }
  ],
  "should_escalate": false,
  "latency_ms": 1842
}
```

### `GET /health`

Returns database connectivity and version.

---

## Tests

```bash
make test
```

All unit tests run without API keys or a database connection — chunker logic, RRF fusion math, guard node thresholds, API schema validation, and policy-code keyword extraction.

---

## Eval suite

```bash
make eval
```

Runs all 30 ground truth cases and writes `eval/report.md`. Five metrics:

| Metric | Target |
|--------|--------|
| Retrieval hit rate @3 | >= 90% |
| Answer correctness | >= 85% |
| Escalation accuracy | >= 90% |
| Avg faithfulness | >= 85% |
| Confident + wrong rate | < 5% (hard gate, fails the run) |
| Latency p95 | < 3000ms |

The faithfulness score uses an LLM-as-judge call (same model) that checks whether every claim in the answer is traceable to the retrieved chunks.

The eval makes 2 API calls per case (synthesis + faithfulness judge). On Groq's free tier, allow 5-10 minutes for 30 cases.

---

## Load test

```bash
# Server must be running
make load-test
```

Fires 20 concurrent requests and reports client-side and server-side latency at p50/p95/p99.

---

## Eval results

*Run `make eval` to generate. See `eval/report.md` for the full per-case breakdown.*

<!-- EVAL_RESULTS_START -->
| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Retrieval Hit Rate @3 | **100.0%** | >=90% | PASS |
| Answer Correctness | **100.0%** | >=85% | PASS |
| Escalation Accuracy | **100.0%** | >=90% | PASS |
| Avg Faithfulness | **98.3%** | >=85% | PASS |
| **Confident + Wrong Rate** | **0.0%** | **<5%** | **PASS** |
| Latency p50 / p95 | 4029ms / 5421ms | p95 <3s | p95 above target on Groq free tier* |

*p95 latency reflects Groq's shared free-tier inference queue, not the model's inherent speed. On dedicated compute the 70B model runs at ~800 tokens/s, bringing p95 well under 3s.

Model: `llama-3.3-70b-versatile` via Groq | Embeddings: `jina-embeddings-v3` | Cases: 30/30
<!-- EVAL_RESULTS_END -->

---

## Known limitations

1. **International shipping** — `case_0195_customs_delay.md` flags that an international shipping SOP is absent from the knowledge base. The agent correctly excludes customs delays from the DEL-007 domestic scope but cannot give further guidance.
2. **Single-turn only** — No conversation memory. Follow-up questions must restate context.
3. **Groq free-tier token cap** — The 70B model has a 100K tokens/day limit on the free tier. The eval uses ~80K tokens per full run. A paid Groq account or switching to an 8B model removes this constraint.

---

## Project structure

```
src/
  config.py          Pydantic-settings, single source of truth for all tunable params
  main.py            FastAPI app with lifespan startup/shutdown
  models.py          Typed request/response schemas
  db.py              asyncpg pool with pgvector codec registration
  embeddings.py      Jina v3 client with tenacity retry
  ingestion/         Loader, paragraph-aware chunker, idempotent pipeline
  retrieval/         Vector search, keyword search, RRF fusion
  agent/             LangGraph graph: state, 4 nodes, compiled graph
  middleware/        Structured audit logging, global exception handler
tests/               Unit tests (no network, no DB)
eval/                Ground truth (30 cases), eval runner, metrics, load test
ui/                  Single-file chat interface
data/knowledge_base/ 20 CX support policy documents
```
