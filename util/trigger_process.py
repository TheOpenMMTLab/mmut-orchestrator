import uuid
import os
import asyncio
import threading
import logging
from typing import List
import json

from .processes import get_processes
from .process_pipeline_builder import Process

logger = logging.getLogger(__name__)


def is_valid_uuid(val, version=4):
    try:
        uuid_obj = uuid.UUID(val, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == val.lower()


def get_mmut_dir():
    """List all MMUT files in the current directory."""
    # Ordner, in dem sich die aktuelle Datei befindet
    util_dir = os.path.dirname(os.path.abspath(__file__))

    # Auflösung des relativen Pfads zu einem absoluten Pfad
    return os.path.abspath(os.path.join(util_dir, '../mmut'))


def run_docker_flow_sync(processes: List[Process], flow_name: str):
    """Run the docker_flow synchronously in a thread"""
    try:
        # Import lazily to avoid initializing Prefect during module import
        # (e.g. while running tests that mock this function).
        from .docker_flow import run_docker_flow

        logger.info("Starting docker_flow")
        # Execute the flow
        run_docker_flow(processes, flow_name=flow_name)
        logger.info("Docker_flow completed")

    except Exception as e:
        logger.error(f"Docker_flow failed, error: {str(e)}",)


def read_info_json(mmut_id: str) -> dict:
    info_json = os.path.join(get_mmut_dir(), mmut_id, 'info.json')
    if os.path.exists(info_json):
        with open(info_json, 'r') as f:
            info = json.load(f)
    else:
        info = {}

    return info


def trigger_process(mmut_id : str):

    # Validate UUID format
    if not is_valid_uuid(mmut_id):
        raise ValueError(f"Invalid MMUT ID format for {mmut_id}")

    # Check if the MMUT directory exists
    mmut_path = os.path.join(get_mmut_dir(), mmut_id)
    if not os.path.exists(mmut_path):
        raise ValueError(f"Path {mmut_path} not found")

    flow_name = f"mmut-{mmut_id}"
    info = read_info_json(mmut_id)
    if 'name' in info:
        flow_name = info['name']

    processes: List[Process] = get_processes(mmut_path)

    # Start the flow in a background thread
    thread = threading.Thread(target=run_docker_flow_sync, args=(processes, flow_name))
    thread.daemon = True
    thread.start()

    return thread
