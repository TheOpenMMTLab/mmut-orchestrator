FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PREFECT_API_HOST=0.0.0.0

WORKDIR /opt/prefect

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prefect.txt /tmp/requirements-prefect.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements-prefect.txt

CMD ["prefect", "server", "start", "--host", "0.0.0.0"]