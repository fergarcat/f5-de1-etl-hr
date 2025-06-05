## redis.py
import os
import redis
import json
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

def cache_partial(user_id, data_type, data):
    key = f"user:{user_id}"
    existing = r.get(key)
    user_data = json.loads(existing) if existing else {}
    user_data[data_type] = data
    r.set(key, json.dumps(user_data))

def retrieve_complete(user_id):
    key = f"user:{user_id}"
    val = r.get(key)
    return json.loads(val) if val else {}

def clear_cache(user_id):
    r.delete(f"user:{user_id}")