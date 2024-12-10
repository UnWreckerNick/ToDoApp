import json
from app.redis_client import redis_client

def get_cached_todos(user_id: int):
    todos = redis_client.get(f"todos_{user_id}")
    if todos:
        return json.loads(todos)
    return None

def cache_todo(user_id: int, todos: list):
    redis_client.set(f"todos_{user_id}", json.dumps(todos), ex=3600)
