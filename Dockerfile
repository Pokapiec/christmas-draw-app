FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
# CMD ["/app/.venv/bin/fastapi", "run"]
CMD ["/app/.venv/bin/gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8080"]
