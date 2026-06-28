import logging
import json
import redis
from typing import Any, Callable, Optional

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class CacheMixin:
    """Utilitários de cache"""
    
    @with_fallback(default_return=None)
    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
        """
        Retorna valor do cache ou executa função e armazena.
        
        Exemplo:
            user = redis.get_or_set("user:1", lambda: db.get_user(1), ttl=300)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        value = self.get(key)
        if value is not None:
            return value
        
        value = func()
        self.set(key, str(value) if not isinstance(value, (dict, list)) else json.dumps(value), ttl)
        return value

    @with_fallback(default_return={})
    def get_or_set_json(self, key: str, func: Callable, ttl: Optional[int] = None) -> dict:
        """Versão para JSON"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        value = self.get_json(key)
        if value is not None:
            return value
        
        value = func()
        self.set_json(key, value, ttl)
        return value

    @with_fallback(default_return=0)
    def delete_pattern(self, pattern: str, batch_size: int = 1000) -> int:
        """Deleta todas chaves que correspondem a um padrão"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        deleted = 0
        cursor = 0
        
        while True:
            cursor, keys = self.scan(cursor=cursor, match=pattern, count=batch_size)
            if keys:
                deleted += self.delete(*keys)
            if cursor == 0:
                break
        
        logger.info(f"Deleted {deleted} keys matching pattern '{pattern}'")
        return deleted