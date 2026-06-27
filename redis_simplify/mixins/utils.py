import logging
import redis
from typing import List, Dict, Optional

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class UtilsMixin:
    """Utilitários avançados"""
    
    @recorded()
    @with_fallback(default_return={})
    def mget(self, keys: List[str]) -> Dict[str, Optional[str]]:
        """Obtém múltiplas chaves de uma vez"""
        if not keys:
            return {}
        
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        values = self.client.mget(keys)
        return dict(zip(keys, values))
    
    @recorded()
    @with_fallback(default_return=False)
    def mset(self, mapping: Dict[str, str], expire_seconds: Optional[int] = None) -> bool:
        """Define múltiplas chaves de uma vez"""
        if not mapping:
            return True
        
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if expire_seconds:
            pipe = self.pipeline()
            for key, value in mapping.items():
                pipe.setex(key, expire_seconds, value)
            pipe.execute()
        else:
            self.client.mset(mapping)
        return True
    
    @recorded()
    @with_fallback(default_return=False)
    def rename_safe(self, old_key: str, new_key: str, overwrite: bool = False) -> bool:
        """Renomeia chave com verificação de segurança"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not overwrite and self.exists(new_key):
            logger.warning(f"Target key {new_key} already exists")
            return False
        
        self.client.rename(old_key, new_key)
        return True
    
    @recorded()
    @with_fallback(default_return=False)
    def copy_key(self, source: str, destination: str, replace: bool = False) -> bool:
        """Copia chave de um lugar para outro"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        return self.client.copy(source, destination, replace=replace)