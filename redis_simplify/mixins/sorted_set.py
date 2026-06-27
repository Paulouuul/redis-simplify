import logging
import redis
from typing import List, Dict, Optional

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class SortedSetMixin:
    """Operações com Sorted Sets Redis"""
    
    @recorded()
    @with_fallback(default_return=0)
    def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Adiciona membros com score a um sorted set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zadd(key, mapping)
    
    @recorded()
    @with_fallback(default_return=[])
    def zrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List:
        """Retorna membros em um intervalo"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrange(key, start, stop, withscores=withscores)
    
    @recorded()
    @with_fallback(default_return=[])
    def zrevrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List:
        """Retorna membros em ordem reversa"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrevrange(key, start, stop, withscores=withscores)
    
    @recorded()
    @with_fallback(default_return=None)
    def zrank(self, key: str, member: str) -> Optional[int]:
        """Retorna a posição do membro"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrank(key, member)
    
    @recorded()
    @with_fallback(default_return=None)
    def zscore(self, key: str, member: str) -> Optional[float]:
        """Retorna o score do membro"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zscore(key, member)
    
    @recorded()
    @with_fallback(default_return=0.0)
    def zincrby(self, key: str, amount: float, member: str) -> float:
        """Incrementa score de um membro"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zincrby(key, amount, member)
    
    @recorded()
    @with_fallback(default_return=0)
    def zrem(self, key: str, *members: str) -> int:
        """Remove membros do sorted set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrem(key, *members)
    
    @recorded()
    @with_fallback(default_return=0)
    def zcard(self, key: str) -> int:
        """Retorna número de membros"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zcard(key)