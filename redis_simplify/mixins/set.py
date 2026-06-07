import logging
from typing import Set

from redis_simplify.mixins.metrics import MetricsMixin

logger = logging.getLogger('redis_simplify.client')

class SetMixin:

    @MetricsMixin._recorded
    def sadd(self, key: str, *values: str) -> int:
        """Adiciona valores a um set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.sadd(key, *values)
        except Exception as e:
            logger.error(f"Error on sadd {key}: {e}")
            return 0
    @MetricsMixin._recorded
    def srem(self, key: str, *values: str) -> int:
        """Remove valores de um set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.srem(key, *values)
        except Exception as e:
            logger.error(f"Erro no srem {key}: {e}")
            return 0
    @MetricsMixin._recorded
    def smembers(self, key: str) -> Set[str]:
        """Retorna todos os membros de um set"""
        if not self._ensure_connection():
            return set()
        try:
            return self.client.smembers(key)
        except Exception as e:
            logger.error(f"Error on smembers {key}: {e}")
            return set()
    @MetricsMixin._recorded
    def sismember(self, key: str, value: str) -> bool:
        """Verifica se valor está no set"""
        if not self._ensure_connection():
            return False
        try:
            result = self.client.sismember(key, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Error on sismember {key}: {e}")
            return False
    @MetricsMixin._recorded
    def scard(self, key: str) -> int:
        """Retorna tamanho do set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.scard(key)
        except Exception as e:
            logger.error(f"Error on scard {key}: {e}")
            return 0