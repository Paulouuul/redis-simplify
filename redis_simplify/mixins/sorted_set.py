import logging
from typing import List, Dict, Optional


from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class SortedSetMixin:
    """Operações com Sorted Sets Redis"""
    @recorded()
    def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Adiciona membros com score a um sorted set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.zadd(key, mapping)
        except Exception as e:
            logger.error(f"Error on zadd {key}: {e}")
            return 0
    @recorded()
    def zrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List:
        """Retorna membros em um intervalo"""
        if not self._ensure_connection():
            return []
        try:
            return self.client.zrange(key, start, stop, withscores=withscores)
        except Exception as e:
            logger.error(f"Error on zrange {key}: {e}")
            return []
    @recorded()
    def zrevrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List:
        """Retorna membros em ordem reversa"""
        if not self._ensure_connection():
            return []
        try:
            return self.client.zrevrange(key, start, stop, withscores=withscores)
        except Exception as e:
            logger.error(f"Error on zrevrange {key}: {e}")
            return []
    @recorded()
    def zrank(self, key: str, member: str) -> Optional[int]:
        """Retorna a posição do membro"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.zrank(key, member)
        except Exception as e:
            logger.error(f"Error on zrank {key}: {e}")
            return None
    @recorded()
    def zscore(self, key: str, member: str) -> Optional[float]:
        """Retorna o score do membro"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.zscore(key, member)
        except Exception as e:
            logger.error(f"Error on zscore {key}: {e}")
            return None
    @recorded()
    def zincrby(self, key: str, amount: float, member: str) -> float:
        """Incrementa score de um membro"""
        if not self._ensure_connection():
            return 0.0
        try:
            return self.client.zincrby(key, amount, member)
        except Exception as e:
            logger.error(f"Error on zincrby {key}: {e}")
            return 0.0
    @recorded()
    def zrem(self, key: str, *members: str) -> int:
        """Remove membros do sorted set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.zrem(key, *members)
        except Exception as e:
            logger.error(f"Error on zrem {key}: {e}")
            return 0
    @recorded()
    def zcard(self, key: str) -> int:
        """Retorna número de membros"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.zcard(key)
        except Exception as e:
            logger.error(f"Error on zcard {key}: {e}")
            return 0