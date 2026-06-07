import logging
from typing import Optional


from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class HashMixin:
    @recorded()
    def hset(self, key: str, field: str, value: str) -> int:
        """Define campo em hash"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.hset(key, field, value)
        except Exception as e:
            logger.error(f"Error on hset {key}: {e}")
            return 0
    @recorded()
    def hget(self, key: str, field: str) -> Optional[str]:
        """Obtém campo de hash"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.hget(key, field)
        except Exception as e:
            logger.error(f"Error on hget {key}: {e}")
            return None
    @recorded()
    def hgetall(self, key: str) -> dict:
        """Obtém todo hash"""
        if not self._ensure_connection():
            return {}
        try:
            return self.client.hgetall(key)
        except Exception as e:
            logger.error(f"Error on hgetall {key}: {e}")
            return {}