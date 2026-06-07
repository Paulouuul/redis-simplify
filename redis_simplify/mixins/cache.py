import logging
import json
from typing import Any, Callable, Optional

logger = logging.getLogger('redis_simplify.client')

class CacheMixin:
    """Utilitários de cache"""
    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
        """
        Retorna valor do cache ou executa função e armazena.
        
        Exemplo:
            user = redis.get_or_set("user:1", lambda: db.get_user(1), ttl=300)
        """
        value = self.get(key)
        if value is not None:
            return value
        
        value = func()
        self.set(key, str(value) if not isinstance(value, (dict, list)) else json.dumps(value), ttl)
        return value

    def get_or_set_json(self, key: str, func: Callable, ttl: Optional[int] = None) -> dict:
        """Versão para JSON"""
        value = self.get_json(key)
        if value is not None:
            return value
        
        value = func()
        self.set_json(key, value, ttl)
        return value

    def delete_pattern(self, pattern: str, batch_size: int = 1000) -> int:
        """Deleta todas chaves que correspondem a um padrão"""
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

    def scan_iter(self, match: Optional[str] = None, count: int = 100):
        """Iterator para varrer chaves sem carregar tudo na memória"""
        cursor = 0
        while True:
            cursor, keys = self.scan(cursor=cursor, match=match, count=count)
            for key in keys:
                yield key
            if cursor == 0:
                break