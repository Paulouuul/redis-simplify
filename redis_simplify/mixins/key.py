# redis_simplify/mixins/key.py
import logging
import redis
from typing import Optional, List, Iterator

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class KeyMixin:
    """Operações gerais com chaves (keys, exists, ttl, etc.)"""
    
    @recorded()
    @with_fallback(default_return=0)
    def delete(self, *keys: str) -> int:
        """Deleta uma ou mais chaves"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.delete(*keys)
    
    @recorded()
    @with_fallback(default_return=False)
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.exists(key))
    
    @recorded()
    @with_fallback(default_return=False)
    def expire(self, key: str, seconds: int) -> bool:
        """Define tempo de expiração em segundos"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.expire(key, seconds))
    
    @recorded()
    @with_fallback(default_return=False)
    def expireat(self, key: str, timestamp: int) -> bool:
        """Define expiração em timestamp Unix"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.expireat(key, timestamp))
    
    @recorded()
    @with_fallback(default_return=-2)
    def ttl(self, key: str) -> int:
        """Retorna tempo restante de expiração em segundos (-1 = sem expiração, -2 = não existe)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.ttl(key)
    
    @recorded()
    @with_fallback(default_return=-2)
    def pttl(self, key: str) -> int:
        """Retorna tempo restante de expiração em milissegundos"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.pttl(key)
    
    @recorded()
    @with_fallback(default_return=False)
    def persist(self, key: str) -> bool:
        """Remove expiração da chave"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.persist(key))
    
    @recorded()
    @with_fallback(default_return=False)
    def rename(self, old_key: str, new_key: str) -> bool:
        """Renomeia uma chave"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        self.client.rename(old_key, new_key)
        return True
    
    @recorded()
    @with_fallback(default_return=False)
    def renamenx(self, old_key: str, new_key: str) -> bool:
        """Renomeia chave apenas se nova chave não existir"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.renamenx(old_key, new_key))
    
    @recorded()
    @with_fallback(default_return="none")
    def type(self, key: str) -> str:
        """Retorna o tipo da chave (string, hash, list, set, zset, none)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.type(key)
    
    @with_fallback(default_return=[])
    def keys(self, pattern: str = "*") -> List[str]:
        """
        Retorna chaves que correspondem ao padrão.
        CUIDADO: Pode bloquear o Redis em grandes bases de dados.
        Use scan_iter() para produção.
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.keys(pattern)
    
    def scan_iter(self, match: str = None, count: int = 100) -> Iterator[str]:
        """
        Itera sobre chaves sem carregar todas na memória.
        RECOMENDADO para grandes bases de dados.
        
        Exemplo:
            for key in client.scan_iter(match="user:*", count=100):
                print(key)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.scan_iter(match=match, count=count)
    
    @recorded()
    @with_fallback(default_return=None)
    def randomkey(self) -> Optional[str]:
        """Retorna uma chave aleatória do banco"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.randomkey()