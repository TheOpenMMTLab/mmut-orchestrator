import uuid
import os
import asyncio
import threading
import logging
from typing import List

from .processes import get_processes
from .process_pipeline_builder import Process
from .docker_flow import docker_flow

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


def run_docker_flow_sync(processes: List[Process]):
    """Run the docker_flow synchronously in a thread"""
    try:
        logger.info("Starting docker_flow")
        # Execute the flow
        docker_flow(processes)
        logger.info("Docker_flow completed")

    except Exception as e:
        logger.error(f"Docker_flow failed, error: {str(e)}",)


def trigger_process(mmut_id : str):

    # Validate UUID format
    if not is_valid_uuid(mmut_id):
        raise ValueError("Invalid MMUT ID format for {mmut_id}")
      

    # Check if the MMUT directory exists
    mmut_path = os.path.join(get_mmut_dir(), mmut_id)
    if not os.path.exists(mmut_path):
        raise ValueError(f"Path {mmut_path} not found")

    processes : List[Process] =  get_processes(mmut_path)

    # Start the flow in a background thread
    thread = threading.Thread(target=run_docker_flow_sync, args=(processes,))
    thread.daemon = True
    thread.start()

    return thread
