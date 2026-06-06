# app/core/redis_client.py
import redis
import os
import logging
from typing import Optional, Set, List
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisClient:
    """Cliente Redis genérico SÍNCRONO - pode ser usado por qualquer parte do sistema"""
    
    def __init__(
       self,
        host: str,
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        decode_responses: bool = True,
        socket_keepalive: bool = True,
        health_check_interval: int = 30
    ):
        # Configuração obrigatória via parâmetros (não lê .env)
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        
        self.decode_responses = decode_responses
        self.socket_keepalive = socket_keepalive
        self.health_check_interval = health_check_interval
        
        self.client: Optional[redis.Redis] = None
        self._connect()
    
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
            logger.info(f"RedisClient síncrono conectado: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Erro ao conectar Redis: {e}")
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
            logger.error(f"Erro no ping: {e}")
            return False
    


    def scan(self, cursor: int = 0, match: Optional[str] = None, count: Optional[int] = None) -> tuple:
        """
        Implementação do comando SCAN do Redis
        Retorna (nova_cursor, lista_de_chaves)
        """
        if not self._ensure_connection():
            return 0, []
        try:
            # Redis-py retorna (cursor, keys)
            return self.client.scan(cursor=cursor, match=match, count=count)
        except Exception as e:
            logger.error(f"Erro no scan: {e}")
            return 0, []
    # ========== OPERAÇÕES DE STRING ==========
    
    def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Define valor de uma chave"""
        if not self._ensure_connection():
            return False
        try:
            if expire_seconds:
                self.client.setex(key, expire_seconds, value)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Erro no set {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Obtém valor de uma chave"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Erro no get {key}: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """Deleta uma ou mais chaves"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Erro no delete {keys}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self._ensure_connection():
            return False
        try:
            result = self.client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Erro no exists {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Define tempo de expiração"""
        if not self._ensure_connection():
            return False
        try:
            result = self.client.expire(key, seconds)
            return bool(result)
        except Exception as e:
            logger.error(f"Erro no expire {key}: {e}")
            return False
    
    def incr(self, key: str) -> int:
        """Incrementa contador"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.incr(key)
        except Exception as e:
            logger.error(f"Erro no incr {key}: {e}")
            return 0
        
    def decr(self, key: str) -> int:
        """Decrementa contador"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.decr(key)
        except Exception as e:
            logger.error(f"Erro no decr {key}: {e}")
            return 0
    
    # ========== OPERAÇÕES DE SET (CONJUNTOS) ==========
    
    def sadd(self, key: str, *values: str) -> int:
        """Adiciona valores a um set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.sadd(key, *values)
        except Exception as e:
            logger.error(f"Erro no sadd {key}: {e}")
            return 0
    
    def srem(self, key: str, *values: str) -> int:
        """Remove valores de um set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.srem(key, *values)
        except Exception as e:
            logger.error(f"Erro no srem {key}: {e}")
            return 0
    
    def smembers(self, key: str) -> Set[str]:
        """Retorna todos os membros de um set"""
        if not self._ensure_connection():
            return set()
        try:
            return self.client.smembers(key)
        except Exception as e:
            logger.error(f"Erro no smembers {key}: {e}")
            return set()
    
    def sismember(self, key: str, value: str) -> bool:
        """Verifica se valor está no set"""
        if not self._ensure_connection():
            return False
        try:
            result = self.client.sismember(key, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Erro no sismember {key}: {e}")
            return False
    
    def scard(self, key: str) -> int:
        """Retorna tamanho do set"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.scard(key)
        except Exception as e:
            logger.error(f"Erro no scard {key}: {e}")
            return 0
    
    # ========== OPERAÇÕES DE HASH ==========
    
    def hset(self, key: str, field: str, value: str) -> int:
        """Define campo em hash"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.hset(key, field, value)
        except Exception as e:
            logger.error(f"Erro no hset {key}: {e}")
            return 0
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """Obtém campo de hash"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.hget(key, field)
        except Exception as e:
            logger.error(f"Erro no hget {key}: {e}")
            return None
    
    def hgetall(self, key: str) -> dict:
        """Obtém todo hash"""
        if not self._ensure_connection():
            return {}
        try:
            return self.client.hgetall(key)
        except Exception as e:
            logger.error(f"Erro no hgetall {key}: {e}")
            return {}
    
    # ========== OPERAÇÕES DE LISTA ==========
    
    def lpush(self, key: str, *values: str) -> int:
        """Adiciona ao início da lista"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Erro no lpush {key}: {e}")
            return 0
    
    def rpush(self, key: str, *values: str) -> int:
        """Adiciona ao final da lista"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Erro no rpush {key}: {e}")
            return 0
    
    def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Retorna range da lista"""
        if not self._ensure_connection():
            return []
        try:
            return self.client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Erro no lrange {key}: {e}")
            return []
    
    # ========== OPERAÇÕES COM JSON ==========
    
    def set_json(self, key: str, data: dict, expire_seconds: Optional[int] = None) -> bool:
        """Armazena dados JSON"""
        return self.set(key, json.dumps(data), expire_seconds)
    
    def get_json(self, key: str) -> Optional[dict]:
        """Recupera dados JSON"""
        value = self.get(key)
        return json.loads(value) if value else None
    
    # ========== OPERAÇÕES DE PIPELINE ==========
    
    def pipeline(self):
        """Retorna pipeline para operações em lote"""
        if not self._ensure_connection():
            return None
        return self.client.pipeline()
    
    # ========== OPERAÇÕES DE ADMIN ==========
    
    def flush_all(self):
        """Limpa tudo (CUIDADO: apenas para testes!)"""
        if not self._ensure_connection():
            return
        try:
            self.client.flushall()
            logger.warning("Redis flushall executado!")
        except Exception as e:
            logger.error(f"Erro no flushall: {e}")
    
    def close(self):
        """Fecha conexão"""
        if self.client:
            self.client.close()
            logger.info("Conexão Redis fechada")