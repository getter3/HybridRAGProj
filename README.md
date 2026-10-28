# Hybrid RAG Learning Project

A hands-on project for learning keyword/BM25 search, vector retrieval, rank fusion,
and reranking. The learner writes most of the implementation; the starter code is
intentionally incomplete.

## Agreed scope

- **Database:** PostgreSQL. The learner provisions and designs the database; this
  repository intentionally contains no database setup, schema, migrations, or
  database connection code yet.
- **Keyword retrieval:** true BM25 using ParadeDB's `pg_search` extension.
- **Vector retrieval:** `pgvector` in PostgreSQL.
- **Reranking:** OpenRouter's rerank endpoint.
- **API:** FastAPI is the starter default and can be changed later.
- **Embeddings and rank fusion:** deliberately undecided; choose these together
  when implementing the related lesson.

The local PostgreSQL connection settings are represented in `.env.example`:
host `localhost`, port `5432`, database `paradedb`, and schema `SMT1db`. Add your
database username and password only to your ignored local `.env` file. PostgreSQL
folds unquoted identifiers to lowercase, so if the schema was created with the
exact mixed-case name `SMT1db`, SQL statements must quote it as `"SMT1db"`.

> Before provisioning a database, check that the chosen PostgreSQL host supports
> `pg_search` and `pgvector`. ParadeDB documents `CREATE EXTENSION pg_search
> CASCADE`; installing the server extension may require administrator/superuser
> access. This project does not run that SQL for you.

## Retrieval flow we will build

```text
documents
  -> load and split into chunks
  -> embed chunks
  -> store chunk text, metadata, and vectors in PostgreSQL

query
  -> BM25 candidates (pg_search)  ─┐
  -> vector candidates (pgvector) ─┴-> rank fusion -> OpenRouter reranking
                                                       -> API response
                                                       -> agent skill/tool later
```

BM25 and vector similarity produce different kinds of scores. We will first
retrieve candidate lists independently, then choose a fusion method (for example
Reciprocal Rank Fusion or normalized weighted scores) and evaluate it before
adding the reranker. The reranker should improve the ordering of a small candidate
set; it does not replace the initial retrieval stages.

## Learning sequence

1. **Database concepts (learner-led):** decide chunk/document fields, vector
   dimensions, extension availability, indexes, and BM25/vector SQL. Bring
   questions or proposed SQL here for discussion; no database is modified by the
   assistant.
2. **Ingestion:** implement loading, chunking, embeddings, and persistence in
   small steps. Compare chunk sizes and overlaps rather than treating defaults as
   universal.
3. **Retrieval:** implement BM25 and vector search separately; inspect each
   result list; then implement and compare rank-fusion strategies.
4. **Reranking:** send a bounded candidate set to OpenRouter and preserve the
   original chunk identifiers and metadata in the response.
5. **API and agent integration:** expose retrieval through FastAPI, define and
   test a stable request/response contract, then package an agent-facing skill or
   tool that calls the API.

## Get started

Install the declared project dependencies and create the local virtual environment:

```bash
uv sync
```

Copy `.env.example` to `.env` when you are ready to configure credentials. Do not
commit `.env`.

Run the starter API:

```bash
uv run --env-file .env uvicorn hybrid_rag.api.main:app --reload --port 8890
```

The health route is usable. The search route deliberately returns `501 Not
Implemented` until the retrieval lesson is completed. Interactive API docs are at
`/docs`.

Run the starter checks:

```bash
uv run pytest
uv run ruff check .
```

## Starter map

- `src/hybrid_rag/api/`: API app and request/response contract.
- `src/hybrid_rag/rag/`: small TODO modules for chunking, embeddings, ingestion,
  retrieval, and reranking.
- `tests/`: a health-route smoke test; add tests as each lesson is implemented.

No `.env` file, database schema, database migration, Docker database, or populated
retrieval implementation is included by design.


## docker related
- created network command
```bash
docker network create smt1net --driver bridge
```

- created the app image
```bash
docker build -t smt1_app:latest .
```

- created the docker compose 
```bash
docker compose -p smt1_service down -d
```