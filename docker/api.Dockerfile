FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt /tmp/requirements-api.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements-api.txt

COPY api.py /app/api.py
COPY scripts /app/scripts
COPY scripts/shared_checksums.py /usr/local/bin/shared_checksums.py

COPY util /app/util
COPY static /app/static

RUN chmod +x /usr/local/bin/shared_checksums.py \
    && chmod +x /app/scripts/shared_checksums.py \
    && chmod +x /app/scripts/run_transformations.py

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8002"]