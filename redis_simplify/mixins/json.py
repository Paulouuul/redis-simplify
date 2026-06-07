import json
import logging
from typing import Optional
from redis_simplify.mixins.metrics import MetricsMixin

logger = logging.getLogger('redis_simplify.client')

class JSONMixin:
    @MetricsMixin._recorded
    def set_json(self, key: str, data: dict, expire_seconds: Optional[int] = None) -> bool:
        """Armazena dados JSON"""
        return self.set(key, json.dumps(data), expire_seconds)
    @MetricsMixin._recorded
    def get_json(self, key: str) -> Optional[dict]:
        """Recupera dados JSON"""
        value = self.get(key)
        return json.loads(value) if value else None