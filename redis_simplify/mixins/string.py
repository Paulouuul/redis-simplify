import logging
from typing import Optional

from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class StringMixin:

    @recorded()
    def set(self, key: str, value: str, expire_seconds: Optional[int] = None, 
            nx: bool = False, xx: bool = False) -> bool:
        """Define uma chave"""
        if not self._ensure_connection():
            return False
        try:
            self.client.set(key, value, ex=expire_seconds, nx=nx, xx=xx)
            return True
        except Exception as e:
            logger.error(f"Set {key}: {e}")
            return False
    @recorded()
    def get(self, key: str) -> Optional[str]:
        """Obtém valor de uma chave"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Error on get {key}: {e}")
            return None
        
    @recorded()
    def incr(self, key: str) -> int:
        """Incrementa contador"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.incr(key)
        except Exception as e:
            logger.error(f"Error on incr {key}: {e}")
            return 0
    @recorded()
    def decr(self, key: str) -> int:
        """Decrementa contador"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.decr(key)
        except Exception as e:
            logger.error(f"Error on decr {key}: {e}")
            return 0