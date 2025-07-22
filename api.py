from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from prefect import flow
import asyncio
import threading
import uuid
from datetime import datetime
from typing import Dict, Any
import logging

# Import the docker_flow from run_transformations
from run_transformations import docker_flow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MMUT Transformation API",
    description="API to trigger Docker-based transformation flows",
    version="1.0.0"
)

# In-memory storage for flow runs (in production, use a proper database)
flow_runs: Dict[str, Dict[str, Any]] = {}

def run_docker_flow_sync():
    """Run the docker_flow synchronously in a thread"""
    try:
        logger.info(f"Starting docker_flow")
        # Execute the flow
        docker_flow()
        logger.info(f"Docker_flow completed")
        
    except Exception as e:
        logger.error(f"Docker_flow failed, error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MMUT Transformation API",
        "version": "1.0.0",
        "endpoints": {
            "trigger_flow": "GET /trigger-flow"
        }
    }

@app.get("/trigger-flow")
async def trigger_flow(background_tasks: BackgroundTasks):
    """
    Trigger the docker_flow transformation process
    """
    
    # Start the flow in a background thread
    thread = threading.Thread(target=run_docker_flow_sync)
    thread.daemon = True
    thread.start()
    
    return JSONResponse(
        status_code=202,
        content={
            "message": "Flow triggered successfully",
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