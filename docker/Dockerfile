FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PREFECT_API_HOST=0.0.0.0 \
    PREFECT_API_URL=http://127.0.0.1:4200/api \
    API_HOST=0.0.0.0 \
    API_PORT=8002

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git age ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# sops installieren
RUN SOPS_VERSION=3.13.1 \
    && ARCH="$(dpkg --print-architecture)" \
    && if [ "$ARCH" = "amd64" ]; then SOPS_ARCH="amd64"; elif [ "$ARCH" = "arm64" ]; then SOPS_ARCH="arm64"; else echo "Unsupported arch: $ARCH" && exit 1; fi \
    && curl -fsSL "https://github.com/getsops/sops/releases/download/v${SOPS_VERSION}/sops-v${SOPS_VERSION}.linux.${SOPS_ARCH}" -o /usr/local/bin/sops \
    && chmod +x /usr/local/bin/sops


# Docker CLI installieren
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-28.3.2.tgz | tar xz 
RUN mv docker/docker /usr/local/bin/ 
RUN rm -rf docker


COPY requirements.txt /tmp/requirements.txt
COPY requirements-api.txt /tmp/requirements-api.txt
COPY requirements-prefect.txt /tmp/requirements-prefect.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY api.py /app/api.py
COPY scripts /app/scripts
COPY util /app/util
COPY static /app/static

COPY docker/start-services.sh /usr/local/bin/start-services.sh

RUN chmod +x /app/scripts/shared_checksums.py \
    && chmod +x /app/scripts/run_transformations.py \
    && chmod +x /usr/local/bin/start-services.sh

EXPOSE 4200 8002
