#redis_simplify/client
import traceback

import redis
import logging
import warnings
from typing import Any, Optional, Callable
from redis_simplify.mixins import AllMixins
logger = logging.getLogger('redis_simplify.client')
logger.addHandler(logging.NullHandler())

class RedisClient(AllMixins):
    """Cliente Redis genérico SÍNCRONO - pode ser usado por qualquer parte do sistema"""
    
    def __init__(
       self,
        host: str,
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        decode_responses: bool = True,
        socket_keepalive: bool = True,
        health_check_interval: int = 30,
        log_level: Optional[str] = None
    ):
        super().__init__()
        # Configuração via parâmetros 
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        
        self.decode_responses = decode_responses
        self.socket_keepalive = socket_keepalive
        self.health_check_interval = health_check_interval

        if log_level:
            self._configure_logging(log_level)
        
        self.client: Optional[redis.Redis] = None
        self._connect()

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
        if hasattr(self.client, name):
            warnings.warn(
                f"Using native Redis method '{name}'. ",
                DeprecationWarning,
                stacklevel=2
            )
            return getattr(self.client, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")