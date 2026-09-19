FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src:/app

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY services ./services
RUN pip install --no-cache-dir ".[services]"

RUN useradd --create-home --uid 10001 appuser
USER appuser
