# MMUT Orchestrator

This application implements an architecture that enables the execution of process models for transforming micro models. The implementation follows the specification defined in https://github.com/TheOpenMMTLab/mmut-execution-system-spec.

## Overview

The orchestrator manages transformation processes for micro models based on process model definitions. It provides:

- A web interface to trigger transformation processes
- Integration with Prefect for workflow orchestration and monitoring
- Visualization of transformation progress through the Prefect UI

## Getting Started

## Installation

Build and start the services with Docker Compose:

```bash
docker compose up --build
```

The compose setup builds dedicated images for the API and Prefect services. Runtime data folders (`config`, `mmut`, `shared`) are mounted into the API container, and the Docker socket is mounted so the orchestrator can start transformation containers.

Stop services:

```bash
docker compose down
```

## Access

- **API/Web Interface**: http://localhost:8002
- **Prefect UI**: http://localhost:4200

## Usage

1. Use the web interface at `localhost:8002` to trigger transformation processes
2. Monitor the transformation process through the Prefect UI at `localhost:4200`


## Scripts

### 1. Run Transformations

Script path: `scripts/run_transformations.py`

Run on host:

```bash
python scripts/run_transformations.py 574ae00d-db14-4e46-82db-c143aa8c1a0f
```

Run inside API container:

```bash
docker compose exec api python /app/scripts/run_transformations.py 574ae00d-db14-4e46-82db-c143aa8c1a0f
```

### 2. Shared Checksums

Script path: `scripts/shared_checksums.py`

Run on host:

```bash
python scripts/shared_checksums.py --shared-path shared
```

Run inside API container:

```bash
docker compose exec api python /app/scripts/shared_checksums.py --shared-path /app/shared
```

Alternative in container (installed helper):

```bash
docker compose exec api python /usr/local/bin/shared_checksums.py --shared-path /app/shared
```


## Trigger Transformations via console

```bash
python scripts/run_transformations.py 574ae00d-db14-4e46-82db-c143aa8c1a0f
```

## Tests

```bash
python -m pytest tests/
```

