FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY src/ ./src/
COPY .env* ./

ENV PYTHONPATH=/app

CMD ["python", "-m", "src.presentation.cli.main"]
