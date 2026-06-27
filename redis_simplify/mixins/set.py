import logging
import redis
from typing import Set

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class SetMixin:

    @recorded()
    @with_fallback(default_return=0)
    def sadd(self, key: str, *values: str) -> int:
        """Adiciona valores a um set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.sadd(key, *values)
    
    @recorded()
    @with_fallback(default_return=0)
    def srem(self, key: str, *values: str) -> int:
        """Remove valores de um set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.srem(key, *values)
    
    @recorded()
    @with_fallback(default_return=set())
    def smembers(self, key: str) -> Set[str]:
        """Retorna todos os membros de um set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.smembers(key)
    
    @recorded()
    @with_fallback(default_return=False)
    def sismember(self, key: str, value: str) -> bool:
        """Verifica se valor está no set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.sismember(key, value))
    
    @recorded()
    @with_fallback(default_return=0)
    def scard(self, key: str) -> int:
        """Retorna tamanho do set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.scard(key)