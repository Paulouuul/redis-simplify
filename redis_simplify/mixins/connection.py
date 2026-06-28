import logging
import redis
from urllib.parse import urlparse
from typing import Optional
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
        

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class ConnectionMixin:
    
    def _get_retry_config(self) -> dict:
        """
        Retorna configuração de retry nativa do redis-py.
        Permite sobrescrever via extra_kwargs.
        """
        # Verifica se o usuário já passou configurações de retry
        if 'retry' in self.extra_kwargs:
            return {}
        
        # Configuração padrão: 3 tentativas com backoff exponencial
        retry = Retry(ExponentialBackoff(), retries=3)
        
        return {
            'retry': retry,
            'retry_on_error': [
                redis.ConnectionError,
                redis.TimeoutError,
                redis.BusyLoadingError,
            ],
        }
    
    def _connect(self):
        """Estabelece conexão com Redis (síncrona)"""
        try:
            # Remove parâmetros específicos do wrapper
            connect_kwargs = self.extra_kwargs.copy()
            connect_kwargs.pop('retry_attempts', None)
            connect_kwargs.pop('backoff_base', None)
            
            # Obtém configurações de retry
            retry_config = self._get_retry_config()
            
            if self._url:
                # Usa URL se disponível
                self.client = redis.Redis.from_url(
                    self._url,
                    decode_responses=self.decode_responses,
                    socket_keepalive=self.socket_keepalive,
                    health_check_interval=self.health_check_interval,
                    **retry_config,
                    **connect_kwargs  # Usa connect_kwargs sem retry_attempts
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
                    **retry_config,
                    **connect_kwargs  # ← Usa connect_kwargs sem retry_attempts
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
                 retry_attempts: int = 3,
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
            retry_attempts: Número de tentativas de reconexão (padrão: 3)
            **kwargs: Parâmetros adicionais para o redis
        
        Returns:
            RedisClient configurado
        
        Exemplos:
            client = RedisClient.from_url('redis://localhost:6379/0')
            client = RedisClient.from_url('redis://:senha@localhost:6379/0')
            client = RedisClient.from_url('rediss://:senha@localhost:6379/0')
            # Com retry customizado
            client = RedisClient.from_url('redis://localhost:6379/0', retry_attempts=5)
        """
        parsed = urlparse(url)
        
        host = parsed.hostname or 'localhost'
        port = parsed.port or 6379
        password = parsed.password
        db = int(parsed.path[1:]) if parsed.path and parsed.path != '/' else 0
        
        # Adiciona retry_attempts aos kwargs se não for o padrão
        if retry_attempts != 3:
            kwargs['retry_attempts'] = retry_attempts
        
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
            fallback_enabled=fallback_enabled,
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
    
    def set_retry_config(self, retries: int = 3, backoff_base: float = 1.0):
        """
        Configura políticas de retry para o cliente.
        
        Args:
            retries: Número máximo de tentativas
            backoff_base: Base do backoff exponencial (em segundos)
        """
        from redis.backoff import ExponentialBackoff
        from redis.retry import Retry
        
        backoff = ExponentialBackoff(base=backoff_base)
        retry = Retry(backoff, retries=retries)
        
        self.extra_kwargs['retry'] = retry
        self.extra_kwargs['retry_on_error'] = [
            redis.ConnectionError,
            redis.TimeoutError,
            redis.BusyLoadingError,
        ]
        
        # Reconecta para aplicar as novas configurações
        self._connect()
        logger.info(f"Retry config updated: {retries} attempts with backoff base {backoff_base}s")


    def set_timeouts(self, socket_timeout: Optional[float] = None,
                 socket_connect_timeout: Optional[float] = None,
                 retry_on_timeout: bool = False):
        """
        Configura timeouts do cliente.
        
        Args:
            socket_timeout: Timeout para operações em segundos
            socket_connect_timeout: Timeout para conexão em segundos
            retry_on_timeout: Se deve tentar novamente em timeout
        """
        if socket_timeout is not None:
            self.extra_kwargs['socket_timeout'] = socket_timeout
        if socket_connect_timeout is not None:
            self.extra_kwargs['socket_connect_timeout'] = socket_connect_timeout
        if retry_on_timeout is not None:
            self.extra_kwargs['retry_on_timeout'] = retry_on_timeout
        
        # Reconecta para aplicar as novas configurações
        self._connect()
        logger.info(f"Timeouts updated: socket_timeout={socket_timeout}, "
                    f"socket_connect_timeout={socket_connect_timeout}, "
                    f"retry_on_timeout={retry_on_timeout}")