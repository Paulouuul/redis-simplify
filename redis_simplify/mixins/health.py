import logging
import time

logger = logging.getLogger('redis_simplify.client')

class HealthMixin:
    """Health check e monitoramento"""
    
    def health_check(self) -> dict:
        """Verifica saúde da conexão Redis"""
        if not self.ping():
            return {"status": "down", "error": "Connection failed"}
        
        try:
            info = self.client.info()
            return {
                "status": "healthy",
                "redis_version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime_days": info.get("uptime_in_days"),
                "keyspace": info.get("db0", {}).get("keys", 0)
            }
        except Exception as e:
            return {"status": "degraded", "error": str(e)}
    
    def ping_latency(self, count: int = 10) -> dict:
        """Mede latência do ping"""
        latencies = []
        
        for _ in range(count):
            start = time.time()
            self.ping()
            latencies.append((time.time() - start) * 1000)
        
        return {
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "avg_ms": round(sum(latencies) / len(latencies), 2),
            "sample_count": count
        }