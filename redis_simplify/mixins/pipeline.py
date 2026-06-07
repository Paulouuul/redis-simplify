import json
import logging
from typing import Optional

logger = logging.getLogger('redis_simplify.client')

class PipelineMixin:
    def pipeline(self):
        """Retorna pipeline para operações em lote"""
        if not self._ensure_connection():
            return None
        return self.client.pipeline()