import json
import uuid
import os
import redis.asyncio as redis

class TaskQueue:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = "taskfabric_queue"

    async def enqueue(self, task_type: str, payload: dict) -> str:
        """Pushes a new task into the queue and stores its initial state."""
        task_id = str(uuid.uuid4())
        task_metadata = {
            "task_id": task_id,
            "type": task_type,
            "payload": json.dumps(payload), # Serialize dict to string
            "status": "pending"
        }
        
        # 1. Save the task metadata in a Redis Hash
        await self.redis.hset(f"task_state:{task_id}", mapping=task_metadata)
        
        # 2. Push the task ID onto the left side of the Redis List
        await self.redis.lpush(self.queue_name, task_id)
        
        print(f"📥 Enqueued: {task_id} | Type: {task_type}")
        return task_id

    async def dequeue(self, timeout=0):
        """Blocks until a task is available, pops it, and returns the data."""
        # 1. Block and pop from the right side of the list (BRPOP)
        result = await self.redis.brpop(self.queue_name, timeout=timeout)
        
        if result:
            _, task_id = result
            
            # 2. Update status to 'processing'
            await self.redis.hset(f"task_state:{task_id}", "status", "processing")
            
            # 3. Fetch the full task details to give to the worker
            task_data = await self.redis.hgetall(f"task_state:{task_id}")
            task_data['payload'] = json.loads(task_data['payload'])
            
            return task_data
        return None

    async def complete_task(self, task_id: str, result_data: dict):
        """Marks a task as finished and stores the result."""
        await self.redis.hset(f"task_state:{task_id}", mapping={
            "status": "completed",
            "result": json.dumps(result_data)
        })
        print(f"✅ Completed: {task_id}")