FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Copy dependency files first (layer cache)
COPY pyproject.toml poetry.lock* ./

# Install runtime deps only (no dev tools in image)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY . .

EXPOSE 8000
