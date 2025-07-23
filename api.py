from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import threading
import os
import json
from datetime import datetime
from typing import Dict, Any
import logging

# Import the docker_flow from run_transformations
from util.docker_flow import docker_flow
from util.helper import get_mmut_dir, is_valid_uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MMUT Transformation API",
    description="API to trigger Docker-based transformation flows",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for flow runs (in production, use a proper database)
flow_runs: Dict[str, Dict[str, Any]] = {}

def run_docker_flow_sync(mmut_id: str):
    """Run the docker_flow synchronously in a thread"""
    try:
        logger.info("Starting docker_flow")
        # Execute the flow
        docker_flow(mmut_id)
        logger.info("Docker_flow completed")
        
    except Exception as e:
        logger.error(f"Docker_flow failed, error: {str(e)}")

@app.get("/")
async def root():
    """Serve the main dashboard page"""
    return FileResponse("static/index.html")


@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "message": "MMUT Transformation API",
        "version": "1.0.0",
        "endpoints": {
            "dashboard": "GET /",
            "api_info": "GET /api/info",
            "trigger_flow_by_id": "GET /trigger-flow/{mmut_id}",
            "trigger_flow_default": "GET /trigger-flow",
            "list_mmut_dags": "GET /list-mmut-dags",
            "health": "GET /health"
        }
    }


@app.get("/list-mmut-dags")
async def list_mmut_dags():
    """List all available mmut dags"""

    dags = []
    for f in os.listdir(get_mmut_dir()):
        id = str(f)
        if is_valid_uuid(id):

            info_json = os.path.join(get_mmut_dir(), id, 'info.json')
            if os.path.exists(info_json):
                with open(info_json, 'r') as f:
                    info = json.load(f)
                    # Assuming info contains a JSON string with a 'name' field
                    # You can parse it if needed
                    # For now, we just use the id as the name
            else:
                info = {}

            dags.append({
                "id": id,
                "info": info
            })
  
    return {
        "dags": dags
    }

@app.get("/trigger-flow/{mmut_id}")
async def trigger_flow_by_id(mmut_id: str, background_tasks: BackgroundTasks):
    """
    Trigger the docker_flow transformation process for a specific MMUT ID
    """
    
    # Validate UUID format
    if not is_valid_uuid(mmut_id):
        return JSONResponse(
            status_code=400,
            content={
                "message": "Invalid MMUT ID format",
                "status": "error"
            }
        )
    
    # Check if the MMUT directory exists
    mmut_dir = os.path.join(get_mmut_dir(), mmut_id)
    if not os.path.exists(mmut_dir):
        return JSONResponse(
            status_code=404,
            content={
                "message": f"MMUT with ID {mmut_id} not found",
                "status": "error"
            }
        )
    
    # Start the flow in a background thread
    thread = threading.Thread(target=run_docker_flow_sync, args=(mmut_id,))
    thread.daemon = True
    thread.start()
    
    return JSONResponse(
        status_code=202,
        content={
            "message": f"Flow for MMUT {mmut_id} triggered successfully",
            "mmut_id": mmut_id,
            "status": "started"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "UP",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)