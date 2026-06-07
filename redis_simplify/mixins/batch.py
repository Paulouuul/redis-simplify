import logging
from typing import List, Optional, Any

logger = logging.getLogger('redis_simplify.client')

class BatchMixin:
    """Operações em lote"""
    
    def batch_get(self, keys: List[str]) -> List[Any]:
        """Obtém múltiplas chaves via pipeline"""
        if not keys:
            return []
        
        if not self._ensure_connection():
            return [None] * len(keys)
        
        try:
            pipe = self.pipeline()
            for key in keys:
                pipe.get(key)
            return pipe.execute()
        except Exception as e:
            logger.error(f"Error in batch_get: {e}")
            return [None] * len(keys)
    
    def batch_set(self, items: List[tuple], expire_seconds: Optional[int] = None) -> bool:
        """Define múltiplas chaves via pipeline"""
        if not items:
            return True
        
        if not self._ensure_connection():
            return False
        
        try:
            pipe = self.pipeline()
            for key, value in items:
                if expire_seconds:
                    pipe.setex(key, expire_seconds, value)
                else:
                    pipe.set(key, value)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Error in batch_set: {e}")
            return False
    
    def batch_delete(self, keys: List[str]) -> int:
        """Deleta múltiplas chaves via pipeline"""
        if not keys:
            return 0
        
        if not self._ensure_connection():
            return 0
        
        try:
            pipe = self.pipeline()
            for key in keys:
                pipe.delete(key)
            results = pipe.execute()
            return sum(results)
        except Exception as e:
            logger.error(f"Error in batch_delete: {e}")
            return 0