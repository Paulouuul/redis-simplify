import logging
import redis
from typing import Optional, Union

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class StringMixin:

    @recorded()
    @with_fallback(default_return=False)
    def set(self, key: str, value: str, expire_seconds: Optional[int] = None, 
            nx: bool = False, xx: bool = False, get: bool = False, 
            keepttl: bool = False) -> Union[bool, Optional[str]]:
        """
        Define uma chave com opções avançadas.
        
        Args:
            key: Nome da chave
            value: Valor a ser armazenado
            expire_seconds: Tempo de expiração em segundos (opcional)
            nx: Só define se a chave não existir
            xx: Só define se a chave já existir
            get: Retorna o valor antigo (Redis 7.0+)
            keepttl: Mantém o TTL existente (Redis 6.0+)
        
        Returns:
            bool: True se sucesso (ou valor antigo se get=True)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        result = self.client.set(key, value, ex=expire_seconds, nx=nx, xx=xx, 
                                get=get, keepttl=keepttl)
        
        if get:
            return result
        return result is not None
    
    @recorded()
    @with_fallback(default_return=None)
    def get(self, key: str, delete: bool = False) -> Optional[str]:
        """
        Obtém valor de uma chave.
        
        Args:
            key: Nome da chave
            delete: Se True, deleta a chave após obter (Redis 6.2+)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if delete:
            return self.client.getdel(key)
        return self.client.get(key)
    
    @recorded()
    @with_fallback(default_return=None)
    def getdel(self, key: str) -> Optional[str]:
        """
        Obtém e deleta uma chave (Redis 6.2+).
        
        Exemplo:
            value = client.getdel("key")
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.getdel(key)
    
    @recorded()
    @with_fallback(default_return=None)
    def getex(self, key: str, ex: Optional[int] = None, px: Optional[int] = None,
              exat: Optional[int] = None, pxat: Optional[int] = None,
              persist: bool = False) -> Optional[str]:
        """
        Obtém e define expiração em uma chave (Redis 6.2+).
        
        Args:
            key: Nome da chave
            ex: Expiração em segundos
            px: Expiração em milissegundos
            exat: Expiração em timestamp Unix (segundos)
            pxat: Expiração em timestamp Unix (milissegundos)
            persist: Remove expiração
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.getex(key, ex=ex, px=px, exat=exat, pxat=pxat, persist=persist)
    
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