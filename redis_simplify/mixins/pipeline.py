import logging
import redis

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class PipelineMixin:
    
    @with_fallback(default_return=None)
    def pipeline(self):
        """Retorna pipeline para operações em lote"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.pipeline()