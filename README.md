# MMUT Orchestrator

This application implements an architecture that enables the execution of process models for transforming micro models. The implementation follows the specification defined in https://github.com/TheOpenMMTLab/mmut-execution-system-spec.

## Overview

The orchestrator manages transformation processes for micro models based on process model definitions. It provides:

- A web interface to trigger transformation processes
- Integration with Prefect for workflow orchestration and monitoring
- Visualization of transformation progress through the Prefect UI

## Getting Started

1. Start the dev container
2. Manually start both applications (see below)

## Starting the Applications

Start Prefect server:
```bash
prefect server start
```

Start API server:
```bash
uvicorn api:app --host 0.0.0.0 --port 8002 --reload
```

## Access

- **API/Web Interface**: http://localhost:8002
- **Prefect UI**: http://localhost:4200

## Usage

1. Use the web interface at `localhost:8002` to trigger transformation processes
2. Monitor the transformation process through the Prefect UI at `localhost:4200`


## Trigger Transformations via console

```bash
python run_transformations.py 574ae00d-db14-4e46-82db-c143aa8c1a0f
```

## Tests

```bash
python -m pytest tests/
```

