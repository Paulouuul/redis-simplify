import logging
import time
import functools
from typing import Dict
from collections import defaultdict

logger = logging.getLogger('redis_simplify.client')

class MetricsMixin:
    """Métricas de performance"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._metrics_enabled = False
        self._metrics = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})

    def _recorded(self, command_name=None):
        """Decorator para registrar métricas automaticamente"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self._metrics_enabled:
                    return func(*args, **kwargs)
                
                start = time.time()
                error = False
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    error = True
                    raise
                finally:
                    duration_ms = (time.time() - start) * 1000
                    cmd = command_name or func.__name__
                    self._record_metric(cmd, duration_ms, error)
            return wrapper
        return decorator
    
    def enable_metrics(self):
        """Habilita coleta de métricas"""
        self._metrics_enabled = True
        logger.info("Metrics collection enabled")
    
    def disable_metrics(self):
        """Desabilita coleta de métricas"""
        self._metrics_enabled = False
    
    def _record_metric(self, command: str, duration_ms: float, error: bool = False):
        if not self._metrics_enabled:
            return
        
        self._metrics[command]["count"] += 1
        self._metrics[command]["total_time"] += duration_ms
        if error:
            self._metrics[command]["errors"] += 1
    
    def get_metrics(self) -> Dict:
        """Retorna métricas coletadas"""
        if not self._metrics_enabled:
            return {"enabled": False, "message": "Enable metrics with enable_metrics()"}
        
        result = {"enabled": True, "commands": {}}
        for cmd, data in self._metrics.items():
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            result["commands"][cmd] = {
                "count": data["count"],
                "avg_time_ms": round(avg_time, 2),
                "errors": data["errors"],
                "error_rate": round(data["errors"] / data["count"] * 100, 2) if data["count"] > 0 else 0
            }
        return result
    
    def reset_metrics(self):
        """Reseta todas as métricas"""
        self._metrics.clear()
        logger.info("Metrics reset")