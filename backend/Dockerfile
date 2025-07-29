FROM python:3.11-slim-bookworm
RUN groupadd -r django && useradd -r -g django django
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*
COPY --chown=django:django . .
USER django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]