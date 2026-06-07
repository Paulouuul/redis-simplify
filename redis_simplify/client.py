#redis_simplify/client
import redis
import logging
import warnings
from typing import Optional, Set, List
import json
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
        self.close()
        
    def __getattr__(self, name):
        if hasattr(self.client, name):
            warnings.warn(
                f"Using native Redis method '{name}'. ",
                DeprecationWarning,
                stacklevel=2
            )
            return getattr(self.client, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")