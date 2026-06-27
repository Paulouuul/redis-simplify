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
        
    @recorded()
    def append(self, key: str, value: str) -> int:
        """Adiciona valor ao final da string. Retorna o novo tamanho."""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.append(key, value)
        except Exception as e:
            logger.error(f"Error on append {key}: {e}")
            return 0

    @recorded()
    def strlen(self, key: str) -> int:
        """Retorna o tamanho da string"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.strlen(key)
        except Exception as e:
            logger.error(f"Error on strlen {key}: {e}")
            return 0

    @recorded()
    def getrange(self, key: str, start: int, end: int) -> str:
        """Retorna substring da posição start até end"""
        if not self._ensure_connection():
            return ""
        try:
            return self.client.getrange(key, start, end)
        except Exception as e:
            logger.error(f"Error on getrange {key}: {e}")
            return ""

    @recorded()
    def setrange(self, key: str, offset: int, value: str) -> int:
        """
        Sobrescreve parte da string a partir do offset.
        Retorna o novo tamanho da string.
        """
        if not self._ensure_connection():
            return 0
        try:
            return self.client.setrange(key, offset, value)
        except Exception as e:
            logger.error(f"Error on setrange {key}: {e}")
            return 0