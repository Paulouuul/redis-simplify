import logging
import redis  # ← Adicione esta importação
from typing import Optional

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class StringMixin:

    @recorded()
    @with_fallback(default_return=False)
    def set(self, key: str, value: str, expire_seconds: Optional[int] = None, 
            nx: bool = False, xx: bool = False) -> bool:
        """Define uma chave"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        self.client.set(key, value, ex=expire_seconds, nx=nx, xx=xx)
        return True
    
    @recorded()
    @with_fallback(default_return=None)
    def get(self, key: str) -> Optional[str]:
        """Obtém valor de uma chave"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.get(key)
    
    @recorded()
    @with_fallback(default_return=0)
    def incr(self, key: str) -> int:
        """Incrementa contador"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.incr(key)
    
    @recorded()
    @with_fallback(default_return=0)
    def decr(self, key: str) -> int:
        """Decrementa contador"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.decr(key)
    
    @recorded()
    @with_fallback(default_return=0)
    def append(self, key: str, value: str) -> int:
        """Adiciona valor ao final da string. Retorna o novo tamanho."""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.append(key, value)

    @recorded()
    @with_fallback(default_return=0)
    def strlen(self, key: str) -> int:
        """Retorna o tamanho da string"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.strlen(key)

    @recorded()
    @with_fallback(default_return="")
    def getrange(self, key: str, start: int, end: int) -> str:
        """Retorna substring da posição start até end"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.getrange(key, start, end)

    @recorded()
    @with_fallback(default_return=0)
    def setrange(self, key: str, offset: int, value: str) -> int:
        """
        Sobrescreve parte da string a partir do offset.
        Retorna o novo tamanho da string.
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.setrange(key, offset, value)