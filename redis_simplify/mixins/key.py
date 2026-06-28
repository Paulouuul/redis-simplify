# redis_simplify/mixins/key.py
import logging
import redis
from typing import Optional, List, Iterator, Union

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class KeyMixin:
    """Operações gerais com chaves (keys, exists, ttl, etc.)"""
    
    @recorded()
    @with_fallback(default_return=0)
    def delete(self, *keys: str) -> int:
        """Deleta uma ou mais chaves"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.delete(*keys)
    
    @recorded()
    @with_fallback(default_return=False)
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.exists(key))
    
    @recorded()
    @with_fallback(default_return=False)
    def expire(self, key: str, seconds: int, 
               nx: bool = False, xx: bool = False, 
               gt: bool = False, lt: bool = False) -> bool:
        """
        Define tempo de expiração em segundos com opções avançadas.
        
        Args:
            key: Nome da chave
            seconds: Tempo de expiração em segundos
            nx: Só define se não tiver expiração (Redis 7.0+)
            xx: Só define se já tiver expiração (Redis 7.0+)
            gt: Só define se novo TTL for maior (Redis 7.0+)
            lt: Só define se novo TTL for menor (Redis 7.0+)
        
        Exemplos:
            client.expire("key", 60)  # Expira em 60s
            client.expire("key", 60, nx=True)  # Só se não tiver expiração
            client.expire("key", 60, gt=True)  # Só se novo TTL > atual
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.expire(key, seconds, nx=nx, xx=xx, gt=gt, lt=lt))
    
    @recorded()
    @with_fallback(default_return=False)
    def expireat(self, key: str, timestamp: int, 
                 nx: bool = False, xx: bool = False, 
                 gt: bool = False, lt: bool = False) -> bool:
        """
        Define expiração em timestamp Unix com opções avançadas.
        
        Args:
            key: Nome da chave
            timestamp: Timestamp Unix de expiração
            nx: Só define se não tiver expiração (Redis 7.0+)
            xx: Só define se já tiver expiração (Redis 7.0+)
            gt: Só define se novo TTL for maior (Redis 7.0+)
            lt: Só define se novo TTL for menor (Redis 7.0+)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.expireat(key, timestamp, nx=nx, xx=xx, gt=gt, lt=lt))
    
    @recorded()
    @with_fallback(default_return=-2)
    def ttl(self, key: str) -> int:
        """
        Retorna tempo restante de expiração em segundos.
        
        Returns:
            -1: Sem expiração
            -2: Chave não existe
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.ttl(key)
    
    @recorded()
    @with_fallback(default_return=-2)
    def pttl(self, key: str) -> int:
        """
        Retorna tempo restante de expiração em milissegundos.
        
        Returns:
            -1: Sem expiração
            -2: Chave não existe
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.pttl(key)
    
    @recorded()
    @with_fallback(default_return=False)
    def persist(self, key: str) -> bool:
        """Remove expiração da chave"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.persist(key))
    
    @recorded()
    @with_fallback(default_return=False)
    def rename(self, old_key: str, new_key: str) -> bool:
        """Renomeia uma chave"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        self.client.rename(old_key, new_key)
        return True
    
    @recorded()
    @with_fallback(default_return=False)
    def renamenx(self, old_key: str, new_key: str) -> bool:
        """Renomeia chave apenas se nova chave não existir"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.renamenx(old_key, new_key))
    
    @recorded()
    @with_fallback(default_return="none")
    def type(self, key: str) -> str:
        """Retorna o tipo da chave (string, hash, list, set, zset, none)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.type(key)
    
    @with_fallback(default_return=[])
    def keys(self, pattern: str = "*") -> List[str]:
        """
        Retorna chaves que correspondem ao padrão.
        CUIDADO: Pode bloquear o Redis em grandes bases de dados.
        Use scan_iter() para produção.
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.keys(pattern)
    
    def scan_iter(self, match: str = None, count: int = 100, 
                  type: Optional[str] = None) -> Iterator[str]:
        """
        Itera sobre chaves sem carregar todas na memória.
        
        Args:
            match: Padrão para filtrar chaves
            count: Número de chaves por iteração
            type: Filtrar por tipo de chave (Redis 6.0+)
                   Ex: 'string', 'hash', 'list', 'set', 'zset'
        
        Exemplo:
            for key in client.scan_iter(match="user:*", count=100, type='hash'):
                print(key)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.scan_iter(match=match, count=count, type=type)
    
    @recorded()
    @with_fallback(default_return=None)
    def randomkey(self) -> Optional[str]:
        """Retorna uma chave aleatória do banco"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.randomkey()
    
    # ============ NOVOS MÉTODOS ============
    
    @recorded()
    @with_fallback(default_return=False)
    def expiretime(self, key: str) -> int:
        """
        Retorna o timestamp Unix de expiração da chave (Redis 7.0+).
        
        Returns:
            -1: Sem expiração
            -2: Chave não existe
            timestamp: Timestamp Unix de expiração
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.expiretime(key)
    
    @recorded()
    @with_fallback(default_return=False)
    def pexpiretime(self, key: str) -> int:
        """
        Retorna o timestamp Unix de expiração em milissegundos (Redis 7.0+).
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.pexpiretime(key)
    
    @recorded()
    @with_fallback(default_return=0)
    def touch(self, *keys: str) -> int:
        """
        Atualiza o tempo de acesso das chaves (Redis 3.2.1+).
        
        Returns:
            int: Número de chaves tocadas
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.touch(*keys)
    
    @recorded()
    @with_fallback(default_return=False)
    def copy(self, source: str, destination: str, 
             replace: bool = False, db: Optional[int] = None) -> bool:
        """
        Copia uma chave para outra (Redis 6.2+).
        
        Args:
            source: Chave de origem
            destination: Chave de destino
            replace: Se True, substitui se destino existir
            db: Banco de dados de destino (opcional)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return bool(self.client.copy(source, destination, replace=replace, db=db))
    
    @recorded()
    @with_fallback(default_return=None)
    def object_idletime(self, key: str) -> Optional[int]:
        """
        Retorna o tempo ocioso da chave em segundos (Redis 2.2.3+).
        
        Returns:
            Tempo ocioso em segundos ou None se erro
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.object_idletime(key)
    
    @recorded()
    @with_fallback(default_return=None)
    def object_refcount(self, key: str) -> Optional[int]:
        """
        Retorna o contador de referências da chave (Redis 2.2.3+).
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.object_refcount(key)
    
    @recorded()
    @with_fallback(default_return=None)
    def object_encoding(self, key: str) -> Optional[str]:
        """
        Retorna o encoding interno da chave (Redis 2.2.3+).
        
        Exemplos de encoding:
            'raw', 'int', 'ziplist', 'hashtable', 'linkedlist'
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.object_encoding(key)