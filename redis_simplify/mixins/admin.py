import logging

from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class AdminMixin:
    @recorded()
    def scan(self, cursor: int = 0, match: str = None, count: int = None) -> tuple:
        """Comando SCAN do Redis"""
        if not self._ensure_connection():
            return 0, []
        try:
            return self.client.scan(cursor=cursor, match=match, count=count)
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return 0, []
        
    @recorded()
    def flush_all(self):
        """Limpa tudo (CUIDADO: apenas para testes!)"""
        if not self._ensure_connection():
            return
        try:
            self.client.flushall()
            logger.warning("Redis flushall executed!")
        except Exception as e:
            logger.error(f"Error on flushall: {e}")