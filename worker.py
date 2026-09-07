import asyncio
from queue_manager import TaskQueue

async def process_task(task_data: dict):
    """Simulates heavy background work (e.g., ML inference, Quant backtesting)."""
    task_id = task_data["task_id"]
    task_type = task_data["type"]
    payload = task_data["payload"]

    print(f"\n⚙️  Processing '{task_type}' | Task ID: {task_id[:8]}...")
    
    # Simulate heavy CPU-bound computation
    await asyncio.sleep(5) 
    
    print(f"✅  Finished '{task_type}' | Task ID: {task_id[:8]}")
    
    # Mock a result payload based on the work done
    return {
        "status": "success",
        "metadata": f"Processed {len(str(payload))} bytes of data",
        "model_confidence": 0.94 # Fake metric for our ML/Quant theme
    }

async def worker_loop():
    """Continuously polls the Redis queue for new tasks."""
    queue = TaskQueue()
    print("👷 Worker node booted up and connected to Redis.")
    print("⏳ Waiting for tasks...")
    
    while True:
        try:
            # 1. Block indefinitely until a task hits the queue
            task_data = await queue.dequeue(timeout=5)
            
            if task_data:
                # 2. Execute the heavy work
                result_data = await process_task(task_data)
                
                # 3. Mark the task as completely finished in Redis
                await queue.complete_task(task_data["task_id"], result_data)
        
        except Exception as e:
            # Fault Tolerance: If one task crashes, don't kill the whole worker
            print(f"❌ Error processing task: {e}")
            await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(worker_loop())