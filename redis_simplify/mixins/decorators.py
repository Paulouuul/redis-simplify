# redis_simplify/mixins/decorators.py
import functools
import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger('redis_simplify.client')

# ============ DECORATORS DE FALLBACK (FUNÇÕES INDEPENDENTES) ============

def with_fallback(default_return: Any = None, log_error: bool = True):
    """..."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self = args[0] if args else None
                fallback_enabled = getattr(self, 'fallback_enabled', True) if self else True
                
                if not fallback_enabled:
                    raise
                
                if log_error:
                    logger.error(f"{func.__name__} error: {e}")
                
                if callable(default_return):
                    return default_return()
                return default_return
        return wrapper
    return decorator


def no_fallback(func: Callable) -> Callable:
    """..."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0] if args else None
        if self:
            original_fallback = getattr(self, 'fallback_enabled', True)
            self.fallback_enabled = False
            try:
                return func(*args, **kwargs)
            finally:
                self.fallback_enabled = original_fallback
        else:
            return func(*args, **kwargs)
    return wrapper


def fallback_value(value: Any):
    """..."""
    return with_fallback(default_return=value)


# ============ DECORATORS DE CACHE ============

def cached(ttl: int = 300, key_prefix: str = "", use_json: bool = True, fallback: Optional[Any] = None):
    """..."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0] if args else None
            if not self:
                return func(*args, **kwargs)
            
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args[1:])
            key_parts.extend(f"{k}:{v}" for k, v in kwargs.items())
            cache_key = ":".join(key_parts)
            
            fallback_enabled = getattr(self, 'fallback_enabled', True)
            
            try:
                if use_json:
                    cached_value = self.get_json(cache_key)
                else:
                    cached_value = self.get(cache_key)
                
                if cached_value is not None:
                    return cached_value
            except Exception as e:
                if not fallback_enabled:
                    raise
                logger.debug(f"Cache miss error: {e}")
            
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if not fallback_enabled:
                    raise
                logger.error(f"Function {func.__name__} error: {e}")
                return fallback
            
            if result is not None:
                try:
                    if use_json:
                        self.set_json(cache_key, result, ttl)
                    else:
                        self.set(cache_key, result, expire_seconds=ttl)
                except Exception as e:
                    if not fallback_enabled:
                        raise
                    logger.debug(f"Cache set error: {e}")
            
            return result
        return wrapper
    return decorator


# ============ DECORATORS DE RATE LIMITING ============

def rate_limited(max_calls: int, per_seconds: int, fallback: Optional[Any] = None):
    """..."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0] if args else None
            if not self:
                return func(*args, **kwargs)
            
            key = f"ratelimit:{func.__name__}"
            fallback_enabled = getattr(self, 'fallback_enabled', True)
            
            try:
                if not self.rate_limit_check(key, max_calls, per_seconds):
                    if not fallback_enabled:
                        raise Exception(f"Rate limit exceeded: {max_calls} calls per {per_seconds}s")
                    
                    logger.warning(f"Rate limit exceeded for {func.__name__}")
                    return fallback
                
                return func(*args, **kwargs)
            except Exception as e:
                if not fallback_enabled:
                    raise
                logger.error(f"Rate limit error for {func.__name__}: {e}")
                return fallback
        return wrapper
    return decorator


# ============ DECORATORS DE RETRY ============

def retry(max_attempts: int = 3, delay: float = 0.5, backoff: float = 2, fallback: Optional[Any] = None):
    """..."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0] if args else None
            current_delay = delay
            last_exception = None
            fallback_enabled = getattr(self, 'fallback_enabled', True) if self else True
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        if not fallback_enabled:
                            raise
                        
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                        return fallback
                    
                    logger.warning(f"Retry {attempt+1}/{max_attempts} for {func.__name__} after error: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return fallback
        return wrapper
    return decorator


# ============ MIXIN COM DECORATORS DE INSTÂNCIA ============

class DecoratorsMixin:
    """Decorators para uso com Redis (métodos de instância)"""
    
    def cached(self, ttl: int = 300, key_prefix: str = "", use_json: bool = True, fallback: Optional[Any] = None):
        """Versão de instância do decorator cached."""
        return cached(ttl=ttl, key_prefix=key_prefix, use_json=use_json, fallback=fallback)
    
    def rate_limited(self, max_calls: int, per_seconds: int, fallback: Optional[Any] = None):
        """Versão de instância do decorator rate_limited."""
        return rate_limited(max_calls=max_calls, per_seconds=per_seconds, fallback=fallback)
    
    def retry(self, max_attempts: int = 3, delay: float = 0.5, backoff: float = 2, fallback: Optional[Any] = None):
        """Versão de instância do decorator retry."""
        return retry(max_attempts=max_attempts, delay=delay, backoff=backoff, fallback=fallback)
    
    def fallback_context(self, enabled: bool = True):
        class FallbackContext:
            def __init__(self, obj, enabled):
                self.obj = obj
                self.enabled = enabled
                self.original = None
            
            def __enter__(self):
                self.original = getattr(self.obj, 'fallback_enabled', True)
                self.obj.fallback_enabled = self.enabled
                return self.obj
            
            def __exit__(self, *args):
                self.obj.fallback_enabled = self.original
        
        return FallbackContext(self, enabled)