import logging
import time
import redis

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class HealthMixin:
    """Health check e monitoramento"""
    
    @with_fallback(default_return={"status": "down", "error": "Connection failed"})
    def health_check(self) -> dict:
        """Verifica saúde da conexão Redis"""
        if not self.ping():
            return {"status": "down", "error": "Connection failed"}
        
        info = self.client.info()
        return {
            "status": "healthy",
            "redis_version": info.get("redis_version"),
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "uptime_days": info.get("uptime_in_days"),
            "keyspace": info.get("db0", {}).get("keys", 0)
        }
    
    @with_fallback(default_return={
        "min_ms": 0,
        "max_ms": 0,
        "avg_ms": 0,
        "sample_count": 0,
        "error": "Failed to measure latency"
    })
    def ping_latency(self, count: int = 10) -> dict:
        """Mede latência do ping"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
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