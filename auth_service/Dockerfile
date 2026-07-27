FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

CMD ["uvicorn", "auth_service:create_app", "--factory", "--host", "0.0.0.0", "--port", "8002"]
