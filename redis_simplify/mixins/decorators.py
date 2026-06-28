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
    """
    Decorator para cache automático.
    
    Args:
        ttl: Tempo de vida do cache em segundos
        key_prefix: Prefixo para a chave do cache
        use_json: Se True, usa JSON serialization
        fallback: Valor a retornar em caso de erro (opcional)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # IMPORTANTE: args contém TODOS os argumentos da função
            # Para @client.cached, args = (5,) quando chamamos func(5)
            # Para funções normais, args = (5,) também
            
            import hashlib
            
            # Gera chave do cache - inclui TODOS os argumentos
            key_parts = [key_prefix, func.__name__]
            
            # Adiciona TODOS os argumentos (NÃO usa args[1:])
            for arg in args:
                key_parts.append(repr(arg))
            
            # Adiciona todos os kwargs ordenados
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}:{repr(v)}")
            
            key_str = ":".join(key_parts)
            cache_key = f"{key_prefix}:{hashlib.md5(key_str.encode()).hexdigest()[:16]}"
            
            # O cliente está disponível via closure (self do método cached)
            # Ou pode ser obtido de outra forma
            redis_client = args[0] if args and hasattr(args[0], 'get') else None
            
            # Se o primeiro argumento for o cliente, usamos ele
            # Senão, tentamos encontrar o cliente de outra forma
            if redis_client is None:
                # Se não for uma função de instância, tenta obter o cliente do contexto
                # Neste caso, o cliente é passado via closure
                import inspect
                frame = inspect.currentframe()
                # Procura por 'self' no frame anterior
                if frame and frame.f_back:
                    local_vars = frame.f_back.f_locals
                    if 'self' in local_vars and hasattr(local_vars['self'], 'get'):
                        redis_client = local_vars['self']
            
            if redis_client is None:
                # Se não encontrou cliente, executa a função sem cache
                logger.warning("No Redis client found for caching, executing function without cache")
                return func(*args, **kwargs)
            
            fallback_enabled = getattr(redis_client, 'fallback_enabled', True)
            
            # Tenta buscar do cache
            try:
                if use_json:
                    cached_value = redis_client.get_json(cache_key)
                else:
                    cached_value = redis_client.get(cache_key)
                
                if cached_value is not None:
                    return cached_value
                
                if redis_client.exists(cache_key):
                    return cached_value
            except Exception as e:
                if not fallback_enabled:
                    raise
                logger.debug(f"Cache miss error for {cache_key}: {e}")
            
            # Executa a função
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if not fallback_enabled:
                    raise
                logger.error(f"Function {func.__name__} error: {e}")
                return fallback
            
            # Salva no cache
            try:
                if use_json:
                    redis_client.set_json(cache_key, result, ttl)
                else:
                    if result is None:
                        redis_client.set(cache_key, "None", expire_seconds=ttl)
                    else:
                        redis_client.set(cache_key, result, expire_seconds=ttl)
            except Exception as e:
                if not fallback_enabled:
                    raise
                logger.debug(f"Cache set error for {cache_key}: {e}")
            
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
    """
    Decorator para retry com backoff exponencial.
    
    Args:
        max_attempts: Número máximo de tentativas
        delay: Delay inicial em segundos
        backoff: Fator de backoff (multiplicador)
        fallback: Valor a retornar em caso de falha (opcional)
    """
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
                    
                    # Última tentativa
                    if attempt == max_attempts - 1:
                        if fallback is not None:
                            logger.warning(f"All {max_attempts} attempts failed for {func.__name__}, using fallback")
                            return fallback
                        
                        # Se fallback_enabled=False, levanta exceção
                        if not fallback_enabled:
                            logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                            raise
                        
                        # Se fallback_enabled=True e sem fallback, levanta exceção
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(f"Retry {attempt+1}/{max_attempts} for {func.__name__} after error: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Se chegou aqui (não deveria), levanta a última exceção
            if last_exception:
                raise last_exception
            return None
        return wrapper
    return decorator


# ============ MIXIN COM DECORATORS DE INSTÂNCIA ============

class DecoratorsMixin:
    """Decorators para uso com Redis (métodos de instância)"""
    
    def cached(self, ttl: int = 300, key_prefix: str = "", use_json: bool = True, fallback: Optional[Any] = None):
        """
        Versão de instância do decorator cached.
        
        Exemplo:
            @client.cached(ttl=10, key_prefix="user")
            def get_user(user_id):
                return db.get_user(user_id)
        """
        # O self é o cliente Redis
        # Retorna o decorator com o cliente já injetado
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                import hashlib
                
                # Gera chave do cache - usa TODOS os argumentos
                key_parts = [key_prefix, func.__name__]
                for arg in args:
                    key_parts.append(repr(arg))
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}:{repr(v)}")
                
                key_str = ":".join(key_parts)
                cache_key = f"{key_prefix}:{hashlib.md5(key_str.encode()).hexdigest()[:16]}"
                
                # Usa o cliente (self) disponível via closure
                redis_client = self
                fallback_enabled = getattr(redis_client, 'fallback_enabled', True)
                
                # Tenta buscar do cache
                try:
                    if use_json:
                        cached_value = redis_client.get_json(cache_key)
                    else:
                        cached_value = redis_client.get(cache_key)
                    
                    if cached_value is not None:
                        return cached_value
                    
                    if redis_client.exists(cache_key):
                        return cached_value
                except Exception as e:
                    if not fallback_enabled:
                        raise
                    logger.debug(f"Cache miss: {e}")
                
                # Executa a função
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    if not fallback_enabled:
                        raise
                    logger.error(f"Function {func.__name__} error: {e}")
                    return fallback
                
                # Salva no cache
                try:
                    if use_json:
                        redis_client.set_json(cache_key, result, ttl)
                    else:
                        if result is None:
                            redis_client.set(cache_key, "None", expire_seconds=ttl)
                        else:
                            redis_client.set(cache_key, result, expire_seconds=ttl)
                except Exception as e:
                    if not fallback_enabled:
                        raise
                    logger.debug(f"Cache set error: {e}")
                
                return result
            return wrapper
        return decorator
    
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