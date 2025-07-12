import redis
import json
from typing import Optional, Any
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

class Cache:
    def __init__(self):
        self.client = redis_client
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        try:
            self.client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False
    
    def delete(self, key: str):
        try:
            self.client.delete(key)
            return True
        except Exception:
            return False

cache = Cache()
