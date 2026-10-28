FROM python:3.14-slim AS base

# pin uv to a specific version
COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /uvx /bin/

WORKDIR /app

# Disable development dependencies
ENV UV_NO_DEV=1

COPY src ./src
COPY pyproject.toml poetry.lock* uv.lock ./

# Install dependencies using uv with the locked versions
RUN uv sync --locked

EXPOSE 8890

# run the application with uvicorn through uv
CMD ["uv", "run", "uvicorn", "hybrid_rag.api.main:app", "--host", "0.0.0.0", "--port", "8890"]
