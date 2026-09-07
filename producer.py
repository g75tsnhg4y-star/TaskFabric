from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from queue_manager import TaskQueue

# Initialize the FastAPI server and our Queue Manager
app = FastAPI(title="TaskFabric Producer API")
queue = TaskQueue()

# Define the expected JSON payload using Pydantic
class TaskRequest(BaseModel):
    task_type: str
    payload: dict

@app.post("/jobs")
async def create_job(request: TaskRequest):
    """
    Accepts a job from the user and immediately pushes it to Redis.
    Returns a task_id instantly without waiting for the job to finish.
    """
    task_id = await queue.enqueue(request.task_type, request.payload)
    
    return {
        "message": "Job accepted and queued",
        "task_id": task_id,
        "status": "pending"
    }

@app.get("/jobs/{task_id}")
async def get_job_status(task_id: str):
    """
    Allows the client to poll for updates on their specific job.
    """
    task_data = await queue.redis.hgetall(f"task_state:{task_id}")
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task_data