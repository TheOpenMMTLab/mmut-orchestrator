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

The compose setup builds a single combined image and starts both services (Prefect + API) inside one container via a startup script. Runtime data folders (`config`, `mmut`, `shared`) are mounted into the container, and the Docker socket is mounted so the orchestrator can start transformation containers.

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

### 3. Prefect Runtimes

Script path: `scripts/prefect_runtimes.py`

Run on host:

```bash
python scripts/prefect_runtimes.py
```

Run inside API container:

```bash
docker compose exec api python /app/scripts/prefect_runtimes.py
```

Optional examples:

```bash
# show task runs for a specific flow run name
python scripts/prefect_runtimes.py --run imperial-cuscus
```

### 4. Graph Properties

Script path: `scripts/graph_properties.py`

Analyze graph properties of a MMUT process model (number of transformations, models, task definitions, connected components, and longest path).

Run on host:

```bash
python scripts/graph_properties.py 833eee11-12f7-400d-ada8-0733c37a5563
```

Run inside API container:

```bash
docker compose exec api python /app/scripts/graph_properties.py 833eee11-12f7-400d-ada8-0733c37a5563
```


## Trigger Transformations via console

```bash
python scripts/run_transformations.py 574ae00d-db14-4e46-82db-c143aa8c1a0f
```

## Tests

```bash
python -m pytest tests/
```

