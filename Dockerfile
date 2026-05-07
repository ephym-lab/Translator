FROM python:3.12-slim

WORKDIR /app

# Install uv (the project's package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into the system Python (no venv needed in Docker)
# RUN uv sync --frozen --no-dev
RUN UV_HTTP_TIMEOUT=600 uv sync --frozen --no-dev

# Copy application code
COPY . .

# Run Alembic migrations then start the server
EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
