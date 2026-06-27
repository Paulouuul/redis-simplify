import json
import logging
from typing import Optional

from redis_simplify.mixins.decorators import with_fallback
from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class JSONMixin:
    
    @with_fallback(default_return=False)
    @recorded()
    def set_json(self, key: str, data: dict, expire_seconds: Optional[int] = None) -> bool:
        """Armazena dados JSON"""
        return self.set(key, json.dumps(data), expire_seconds)
    
    @with_fallback(default_return=None)
    @recorded()
    def get_json(self, key: str) -> Optional[dict]:
        """Recupera dados JSON"""
        value = self.get(key)
        return json.loads(value) if value else None