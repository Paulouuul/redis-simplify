import logging
import time
import redis

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class RateLimitMixin:
    """Rate limiting utilities"""
    
    @with_fallback(default_return=False)
    def rate_limit_check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Verifica se pode executar ação (Sliding Window)
        Retorna True se permitido, False se excedeu
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        now = time.time()
        window_key = f"ratelimit:{key}:{int(now / window_seconds)}"
        
        current = self.incr(window_key)
        if current == 1:
            self.expire(window_key, window_seconds)
        
        return current <= max_requests
    
    @with_fallback(default_return=0)
    def rate_limit_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Retorna quantas requisições ainda podem ser feitas"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        now = time.time()
        window_key = f"ratelimit:{key}:{int(now / window_seconds)}"
        
        current = self.get(window_key)
        current = int(current) if current else 0
        return max(0, max_requests - current)
    
    @with_fallback(default_return=0)
    def rate_limit_reset(self, key: str, window_seconds: int) -> int:
        """Retorna segundos até o reset do rate limit"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        now = time.time()
        current_window = int(now / window_seconds)
        next_window = (current_window + 1) * window_seconds
        return int(next_window - now)