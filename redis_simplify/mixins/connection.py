import logging
import redis

logger = logging.getLogger('redis_simplify.client')

class ConnectionMixin:
    def _connect(self):
        """Estabelece conexão com Redis (síncrona)"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password or None,
                db=self.db,
                decode_responses=self.decode_responses,
                socket_keepalive=self.socket_keepalive,
                health_check_interval=self.health_check_interval
            )
                # Testa conexão
            self.client.ping()
            logger.info(f"RedisClient connected: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            self.client = None

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
    

    def ping(self) -> bool:
        """Testa conectividade"""
        if not self._ensure_connection():
            return False
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Ping error: {e}")
            return False
        

    def close(self):
        """Fecha conexão"""
        self.close_pubsubs()
        if self.client:
            self.client.close()
            logger.info("Redis connection closed!")