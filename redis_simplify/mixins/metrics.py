import logging
from typing import Dict
from collections import defaultdict

logger = logging.getLogger('redis_simplify.client')

class MetricsMixin:
    """Métricas de performance"""
    
    def __init__(self, *args, **kwargs):
        # Extrai argumentos específicos do MetricsMixin
        self._metrics_enabled = kwargs.pop('metrics_enabled', False)
        self._metrics = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})
        
        # NÃO passa kwargs adiante (é o último mixin)
        # super().__init__() sem argumentos
        super().__init__()

    def enable_metrics(self):
        """Habilita coleta de métricas"""
        self._metrics_enabled = True
        logger.info("Metrics collection enabled")
    
    def disable_metrics(self):
        """Desabilita coleta de métricas"""
        self._metrics_enabled = False
        logger.info("Metrics collection disabled")
    
    def _record_metric(self, command: str, duration_ms: float, error: bool = False):
        """Registra uma métrica (só funciona se enabled)"""
        if not self._metrics_enabled:
            return
        
        self._metrics[command]["count"] += 1
        self._metrics[command]["total_time"] += duration_ms
        if error:
            self._metrics[command]["errors"] += 1
        
        # Debug: mostra o que está sendo registrado
        logger.debug(f"Metric recorded: {command} = {duration_ms:.2f}ms (error={error})")
    
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