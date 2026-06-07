import logging
from typing import List


from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class ListMixin:
    @recorded()
    def lpush(self, key: str, *values: str) -> int:
        """Adiciona ao início da lista"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Error on lpush {key}: {e}")
            return 0
    @recorded()
    def rpush(self, key: str, *values: str) -> int:
        """Adiciona ao final da lista"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Error on rpush {key}: {e}")
            return 0
    @recorded()
    def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Retorna range da lista"""
        if not self._ensure_connection():
            return []
        try:
            return self.client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Error on lrange {key}: {e}")
            return []