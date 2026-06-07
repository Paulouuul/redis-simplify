"""Decorators para métricas - Função independente"""

import time
import functools
from typing import Callable, Any

def recorded(command_name: str = None) -> Callable:
    """
    Decorator para registrar métricas automaticamente.
    Só registra quando as métricas estão habilitadas.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            start = time.time()
            error = False
            try:
                result = func(self, *args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise
            finally:
                # ⚠️ IMPORTANTE: Só registra se métricas estiverem habilitadas
                if hasattr(self, '_metrics_enabled') and self._metrics_enabled:
                    duration_ms = (time.time() - start) * 1000
                    cmd = command_name or func.__name__
                    if hasattr(self, '_record_metric'):
                        self._record_metric(cmd, duration_ms, error)
        return wrapper
    return decorator