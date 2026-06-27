import logging
import redis
from typing import List, Optional, Any

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class BatchMixin:
    """Operações em lote"""
    
    @with_fallback(default_return=[])
    def batch_get(self, keys: List[str]) -> List[Any]:
        """Obtém múltiplas chaves via pipeline"""
        if not keys:
            return []
        
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        pipe = self.pipeline()
        if pipe is None:
            logger.error("Failed to create pipeline")
            return [None] * len(keys)
        
        for key in keys:
            pipe.get(key)
        return pipe.execute()
    
    @with_fallback(default_return=False)
    def batch_set(self, items: List[tuple], expire_seconds: Optional[int] = None) -> bool:
        """Define múltiplas chaves via pipeline"""
        if not items:
            return True
        
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        pipe = self.pipeline()
        if pipe is None:
            logger.error("Failed to create pipeline")
            return False
        
        for key, value in items:
            if expire_seconds:
                pipe.setex(key, expire_seconds, value)
            else:
                pipe.set(key, value)
        pipe.execute()
        return True
    
    @with_fallback(default_return=0)
    def batch_delete(self, keys: List[str]) -> int:
        """Deleta múltiplas chaves via pipeline"""
        if not keys:
            return 0
        
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        pipe = self.pipeline()
        if pipe is None:
            logger.error("Failed to create pipeline")
            return 0
        
        for key in keys:
            pipe.delete(key)
        results = pipe.execute()
        return sum(results)