"""
WebSocket Routes for Real-time Progress Updates
"""
import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis
from config import settings

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections[task_id] = websocket
    
    def disconnect(self, task_id: str):
        """Remove a WebSocket connection."""
        if task_id in self.active_connections:
            del self.active_connections[task_id]
    
    async def send_personal_message(self, message: Dict[str, Any], task_id: str):
        """Send a message to a specific connection."""
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_json(message)
            except Exception:
                # Connection may have closed
                self.disconnect(task_id)


manager = ConnectionManager()


async def subscribe_to_redis(task_id: str, websocket: WebSocket):
    """Subscribe to Redis pub/sub for task progress updates."""
    redis_client = None
    pubsub = None
    
    try:
        # Create async Redis client
        redis_client = await aioredis.from_url(str(settings.REDIS_URL))
        pubsub = redis_client.pubsub()
        
        # Subscribe to task-specific channel
        channel = f"task-progress:{task_id}"
        await pubsub.subscribe(channel)
        
        # Also check Redis key directly for initial state
        progress_key = f"celery-task-progress:{task_id}"
        initial_data = await redis_client.get(progress_key)
        if initial_data:
            try:
                progress = json.loads(initial_data)
                await websocket.send_json(progress)
            except json.JSONDecodeError:
                pass
        
        # Listen for messages
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = message.get('data')
                    if isinstance(data, bytes):
                        try:
                            progress = json.loads(data)
                            try:
                                await websocket.send_json(progress)
                            except (WebSocketDisconnect, Exception):
                                break
                            
                            # Stop if task is complete or failed
                            if progress.get('status') in ('SUCCESS', 'FAILURE'):
                                break
                        except json.JSONDecodeError:
                            pass
                
                # Check if WebSocket is still connected (non-blocking)
                # We'll rely on the exception handling for disconnects
            except asyncio.TimeoutError:
                # Check Redis key periodically as fallback
                progress_data = await redis_client.get(progress_key)
                if progress_data:
                    try:
                        progress = json.loads(progress_data)
                        try:
                            await websocket.send_json(progress)
                        except (WebSocketDisconnect, Exception):
                            break
                        if progress.get('status') in ('SUCCESS', 'FAILURE'):
                            break
                    except json.JSONDecodeError:
                        pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        # Send error to client
        try:
            await websocket.send_json({
                "status": "ERROR",
                "error": str(e)
            })
        except Exception:
            pass
    finally:
        # Cleanup
        if pubsub:
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except Exception:
                pass
        if redis_client:
            try:
                await redis_client.close()
            except Exception:
                pass
        manager.disconnect(task_id)


@router.websocket("/task/{task_id}")
async def websocket_task_progress(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time task progress updates.
    
    Connects to Redis pub/sub to stream progress updates for a specific task.
    """
    await manager.connect(websocket, task_id)
    
    try:
        await subscribe_to_redis(task_id, websocket)
    except WebSocketDisconnect:
        manager.disconnect(task_id)
    except Exception as e:
        manager.disconnect(task_id)
        try:
            await websocket.send_json({
                "status": "ERROR",
                "error": str(e)
            })
        except Exception:
            pass

