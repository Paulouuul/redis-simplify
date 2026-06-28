# redis_simplify/client.py
import traceback
import logging
import warnings
from typing import Any, Optional, Callable
from redis_simplify.mixins import AllMixins

logger = logging.getLogger('redis_simplify.client')
logger.addHandler(logging.NullHandler())

class RedisClient(AllMixins):
    """Cliente Redis genérico SÍNCRONO - pode ser usado por qualquer parte do sistema"""
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 6379,
                 password: Optional[str] = None,
                 db: int = 0,
                 decode_responses: bool = True,
                 socket_keepalive: bool = True,
                 health_check_interval: int = 30,
                 log_level: Optional[str] = None,
                 fallback_enabled: bool = True,
                 retry_attempts: int = 3,
                 **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.decode_responses = decode_responses
        self.socket_keepalive = socket_keepalive
        self.health_check_interval = health_check_interval
        self.extra_kwargs = kwargs
        self._url = None
        self.client = None
        self.fallback_enabled = fallback_enabled
        self.retry_attempts = retry_attempts
        
        if log_level:
            self._configure_logging(log_level)
        
        self._connect()

    # ============ MÉTODOS AUXILIARES PARA FALLBACK ============
    
    def with_fallback(self, operation: Callable, *args, fallback_value: Any = None, **kwargs) -> Any:
        """
        Executa uma operação COM fallback.
        """
        try:
            result = operation(*args, **kwargs)
            # Se o resultado for None e for uma operação de get, consideramos como fallback
            if result is None and operation.__name__ in ['get', 'get_json', 'hget']:
                return fallback_value
            return result
        except Exception as e:
            logger.error(f"Operation {operation.__name__} failed: {e}")
            return fallback_value
    
    def without_fallback(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Executa uma operação SEM fallback (levanta exceção em caso de erro).
        """
        try:
            result = operation(*args, **kwargs)
            # Se o resultado for None e for uma operação de get, levantamos exceção
            if result is None and operation.__name__ in ['get', 'get_json', 'hget']:
                raise ValueError(f"Key not found for {operation.__name__}")
            return result
        except Exception as e:
            # Se já for uma exceção, relança
            raise
    
    def with_fallback_context(self, enabled: bool = True):
        """
        Context manager para controlar fallback temporariamente.
        """
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
    
    def run_with_fallback(self, operation: Callable, *args, default: Any = None, **kwargs) -> Any:
        """
        Executa uma operação com fallback.
        """
        return self.with_fallback(operation, *args, fallback_value=default, **kwargs)
    
    def safe_get(self, key: str, default: Any = None) -> Any:
        """
        Get com fallback (atalho).
        """
        try:
            # Verifica se o cliente está disponível
            if not self.client:
                logger.error("Redis client not available")
                return default
            return self.with_fallback(self.get, key, fallback_value=default)
        except Exception as e:
            logger.error(f"safe_set error: {e}")
            return default
    
    def safe_set(self, key: str, value: str, default: bool = False, **kwargs) -> bool:
        """
        Set com fallback (atalho).
        """
        try:
            # Verifica se o cliente está disponível
            if not self.client:
                logger.error("Redis client not available")
                return default
            result = self.set(key, value, **kwargs)
            return result if result is not None else default
        except Exception as e:
            logger.error(f"safe_set error: {e}")
            return default
    
    # ============ MÉTODOS DE RETRY ============
    
    def set_retry_attempts(self, attempts: int, backoff_base: float = 1.0):
        """
        Configura o número de tentativas de reconexão.
        
        Args:
            attempts: Número máximo de tentativas (padrão: 3)
            backoff_base: Base do backoff exponencial em segundos (padrão: 1.0)
        
        Exemplo:
            client.set_retry_attempts(5, backoff_base=2.0)
        """
        self.retry_attempts = attempts
        self.extra_kwargs['retry_attempts'] = attempts
        self.extra_kwargs['backoff_base'] = backoff_base
        
        # Reconecta para aplicar novas configurações
        self._connect()
        logger.info(f"Retry attempts set to {attempts} with backoff base {backoff_base}s")

    # ============ MÉTODOS DE LOGGING ============
    
    def _configure_logging(self, log_level: str):
        """Configura o nível de logging do cliente"""
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)
        logger.debug(f"Log level set to {log_level.upper()}")

    def set_log_level(self, level: str):
        """Permite mudar o log level após a criação do cliente"""
        level_upper = level.upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        if level_upper not in valid_levels:
            logger.warning(f"Invalid log level: {level}. Using INFO as fallback.")
            level_upper = "INFO"
        
        log_level = getattr(logging, level_upper)
        logger.setLevel(log_level)
        logger.info(f"Log level changed to {level_upper}")
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Error on block with: {exc_type.__name__}: {exc_val}")
            logger.error(f"Traceback: {''.join(traceback.format_tb(exc_tb))}")
        self.close()
    
    def run_with_rate_limit(self, operation: Callable, rate_key: str, 
                        max_requests: int, window_seconds: int,
                        *args, **kwargs) -> Any:
        """
        Executa uma operação com rate limit.
        
        Args:
            operation: A operação a ser executada (ex: self.set, self.get, self.sadd)
            rate_key: Chave para o rate limit
            max_requests: Número máximo de requisições permitidas
            window_seconds: Janela de tempo em segundos
            *args, **kwargs: Argumentos para a operação
        
        Returns:
            Resultado da operação ou None se rate limit excedeu
        
        Exemplos:
            # Set com rate limit
            success = redis.with_rate_limit(redis.set, "api:user", 10, 60, "key", "value")
            
            # Get com rate limit
            data = redis.with_rate_limit(redis.get, "api:user", 10, 60, "key")
            
            # Sadd com rate limit
            count = redis.with_rate_limit(redis.sadd, "api:user", 10, 60, "set", "a", "b")
        """
        if not self.rate_limit_check(rate_key, max_requests, window_seconds):
            logger.warning(f"Rate limit exceeded for {rate_key}")
            return None
        
        return operation(*args, **kwargs)
    
    def __getattr__(self, name):
        """
        Redireciona chamadas para métodos Redis nativos.
        Apenas para métodos que não existem no wrapper.
        """
        # Verifica se o método existe no cliente Redis
        if hasattr(self.client, name):
            warnings.warn(
                f"Using native Redis method '{name}'. ",
                DeprecationWarning,
                stacklevel=2
            )
            return getattr(self.client, name)
        
        # Se não existir, levanta AttributeError
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")