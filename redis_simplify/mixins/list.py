import logging
import redis
from typing import List

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class ListMixin:
    
    @recorded()
    @with_fallback(default_return=0)
    def lpush(self, key: str, *values: str) -> int:
        """Adiciona ao início da lista"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.lpush(key, *values)
    
    @recorded()
    @with_fallback(default_return=0)
    def rpush(self, key: str, *values: str) -> int:
        """Adiciona ao final da lista"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.rpush(key, *values)
    
    @recorded()
    @with_fallback(default_return=[])
    def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Retorna range da lista"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.lrange(key, start, end)