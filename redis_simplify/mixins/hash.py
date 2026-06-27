import logging
import redis
from typing import Optional

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class HashMixin:
    
    @recorded()
    @with_fallback(default_return=0)
    def hset(self, key: str, field: str, value: str) -> int:
        """Define campo em hash"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.hset(key, field, value)
    
    @recorded()
    @with_fallback(default_return=None)
    def hget(self, key: str, field: str) -> Optional[str]:
        """Obtém campo de hash"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.hget(key, field)
    
    @recorded()
    @with_fallback(default_return={})
    def hgetall(self, key: str) -> dict:
        """Obtém todo hash"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.hgetall(key)