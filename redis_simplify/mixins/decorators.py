import functools
import time
import logging
import json  # ← Adicionar este import
from typing import Callable, Optional

logger = logging.getLogger('redis_simplify.client')

class DecoratorsMixin:
    """Decorators para uso com Redis"""
    
    def cached(self, ttl: int = 300, key_prefix: str = "", use_json: bool = True):
        """
        Decorator para cache automático.
        
        Exemplo:
            @redis.cached(ttl=60)
            def get_user(user_id):
                return db.get_user(user_id)
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Gera chave baseada nos argumentos
                key_parts = [key_prefix, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in kwargs.items())
                cache_key = ":".join(key_parts)
                
                # Tenta pegar do cache (sempre tentar JSON primeiro para preservar tipos)
                cached = self.get_json(cache_key)
                if cached is not None:
                    return cached
                
                # Fallback para string se não encontrar JSON
                if not use_json:
                    cached_str = self.get(cache_key)
                    if cached_str is not None:
                        return cached_str
                
                # Executa função
                result = func(*args, **kwargs)
                
                # Armazena no cache (sempre usar JSON para preservar tipos)
                self.set_json(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    def rate_limited(self, max_calls: int, per_seconds: int):
        """
        Decorator para rate limiting.
        
        Exemplo:
            @redis.rate_limited(max_calls=10, per_seconds=60)
            def api_endpoint():
                return response
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = f"ratelimit:{func.__name__}"
                if not self.rate_limit_check(key, max_calls, per_seconds):
                    raise Exception(f"Rate limit exceeded: {max_calls} calls per {per_seconds}s")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def retry(self, max_attempts: int = 3, delay: float = 0.5, backoff: float = 2):
        """
        Decorator para retry automático.
        
        Exemplo:
            @redis.retry(max_attempts=3)
            def unstable_operation():
                ...
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise
                        logger.warning(f"Retry {attempt+1}/{max_attempts} after error: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                return None
            return wrapper
        return decorator