import logging
import redis
from urllib.parse import urlparse
from typing import Optional

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class ConnectionMixin:
    
    def _connect(self):
        """Estabelece conexão com Redis (síncrona)"""
        try:
            if self._url:
                # Usa URL se disponível
                self.client = redis.Redis.from_url(
                    self._url,
                    decode_responses=self.decode_responses,
                    socket_keepalive=self.socket_keepalive,
                    health_check_interval=self.health_check_interval,
                    **self.extra_kwargs
                )
                # Atualiza host/port para logging
                conn_kwargs = self.client.connection_pool.connection_kwargs
                self.host = conn_kwargs.get('host', self.host)
                self.port = conn_kwargs.get('port', self.port)
            else:
                # Usa parâmetros normais
                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password or None,
                    db=self.db,
                    decode_responses=self.decode_responses,
                    socket_keepalive=self.socket_keepalive,
                    health_check_interval=self.health_check_interval,
                    **self.extra_kwargs
                )
            
            # Testa conexão
            self.client.ping()
            logger.info(f"RedisClient connected: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            self.client = None
    
    @with_fallback(default_return=None)
    def update_url(self, url: str, **kwargs):
        """
        Reconfigura a conexão usando URL.
        
        Args:
            url: URL do Redis (ex: redis://:senha@localhost:6379/0)
            **kwargs: Parâmetros adicionais para a conexão
        
        Returns:
            self (para encadeamento)
        """
        # Atualiza parâmetros extras se fornecidos
        if kwargs:
            self.extra_kwargs.update(kwargs)
        
        # Guarda URL
        self._url = url
        
        # Reconecta usando a URL
        self._connect()
        
        return self

    @classmethod
    def from_url(cls, url: str, 
                 decode_responses: bool = True,
                 socket_keepalive: bool = True,
                 health_check_interval: int = 30,
                 log_level: Optional[str] = None,
                 fallback_enabled: bool = True,
                 **kwargs):
        """
        Cria uma instância do RedisClient a partir de uma URL.
        
        Args:
            url: URL de conexão (ex: redis://:senha@localhost:6379/0)
            decode_responses: Decodificar respostas para string
            socket_keepalive: Manter socket vivo
            health_check_interval: Intervalo de health check
            log_level: Nível de logging
            fallback_enabled: Se True, fallback ativado; Se False, levanta exceções
            **kwargs: Parâmetros adicionais para o redis
        
        Returns:
            RedisClient configurado
        
        Exemplos:
            client = RedisClient.from_url('redis://localhost:6379/0')
            client = RedisClient.from_url('redis://:senha@localhost:6379/0')
            client = RedisClient.from_url('rediss://:senha@localhost:6379/0')
        """
        parsed = urlparse(url)
        
        host = parsed.hostname or 'localhost'
        port = parsed.port or 6379
        password = parsed.password
        db = int(parsed.path[1:]) if parsed.path and parsed.path != '/' else 0
        
        # Cria instância
        instance = cls(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=decode_responses,
            socket_keepalive=socket_keepalive,
            health_check_interval=health_check_interval,
            log_level=log_level,
            fallback_enabled=fallback_enabled,  # ← VÍRGULA ADICIONADA
            **kwargs
        )
        
        # Guarda URL e reconecta
        instance._url = url
        instance._connect()
        
        return instance

    @with_fallback(default_return=False)
    def _ensure_connection(self) -> bool:
        """Verifica conexão e tenta reconectar se necessário"""
        if self.client:
            try:
                self.client.ping()
                return True
            except Exception:
                self.client = None
        
        self._connect()
        return self.client is not None

    @with_fallback(default_return=False)
    def ping(self) -> bool:
        """Testa conectividade"""
        if not self._ensure_connection():
            return False
        return self.client.ping()

    @with_fallback(default_return=None)
    def close(self):
        """Fecha conexão"""
        if hasattr(self, 'close_pubsubs'):
            self.close_pubsubs()
        
        if self.client:
            self.client.close()
            logger.info("Redis connection closed!")