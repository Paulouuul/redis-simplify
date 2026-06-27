# redis_simplify/mixins/key.py
import logging
from typing import Optional, List, Iterator
from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class KeyMixin:
    """Operações gerais com chaves (keys, exists, ttl, etc.)"""
    
    @recorded()
    def delete(self, *keys: str) -> int:
        """Deleta uma ou mais chaves"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Error on delete {keys}: {e}")
            return 0
    
    @recorded()
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self._ensure_connection():
            return False
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error on exists {key}: {e}")
            return False
    
    @recorded()
    def expire(self, key: str, seconds: int) -> bool:
        """Define tempo de expiração em segundos"""
        if not self._ensure_connection():
            return False
        try:
            return bool(self.client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Error on expire {key}: {e}")
            return False
    
    @recorded()
    def expireat(self, key: str, timestamp: int) -> bool:
        """Define expiração em timestamp Unix"""
        if not self._ensure_connection():
            return False
        try:
            return bool(self.client.expireat(key, timestamp))
        except Exception as e:
            logger.error(f"Error on expireat {key}: {e}")
            return False
    
    @recorded()
    def ttl(self, key: str) -> int:
        """Retorna tempo restante de expiração em segundos (-1 = sem expiração, -2 = não existe)"""
        if not self._ensure_connection():
            return -2
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Error on ttl {key}: {e}")
            return -2
    
    @recorded()
    def pttl(self, key: str) -> int:
        """Retorna tempo restante de expiração em milissegundos"""
        if not self._ensure_connection():
            return -2
        try:
            return self.client.pttl(key)
        except Exception as e:
            logger.error(f"Error on pttl {key}: {e}")
            return -2
    
    @recorded()
    def persist(self, key: str) -> bool:
        """Remove expiração da chave"""
        if not self._ensure_connection():
            return False
        try:
            return bool(self.client.persist(key))
        except Exception as e:
            logger.error(f"Error on persist {key}: {e}")
            return False
    
    @recorded()
    def rename(self, old_key: str, new_key: str) -> bool:
        """Renomeia uma chave"""
        if not self._ensure_connection():
            return False
        try:
            self.client.rename(old_key, new_key)
            return True
        except Exception as e:
            logger.error(f"Error on rename {old_key} to {new_key}: {e}")
            return False
    
    @recorded()
    def renamenx(self, old_key: str, new_key: str) -> bool:
        """Renomeia chave apenas se nova chave não existir"""
        if not self._ensure_connection():
            return False
        try:
            return bool(self.client.renamenx(old_key, new_key))
        except Exception as e:
            logger.error(f"Error on renamenx {old_key} to {new_key}: {e}")
            return False
    
    @recorded()
    def type(self, key: str) -> str:
        """Retorna o tipo da chave (string, hash, list, set, zset, none)"""
        if not self._ensure_connection():
            return "none"
        try:
            return self.client.type(key)
        except Exception as e:
            logger.error(f"Error on type {key}: {e}")
            return "none"
    
    def keys(self, pattern: str = "*") -> List[str]:
        """
        Retorna chaves que correspondem ao padrão.
        CUIDADO: Pode bloquear o Redis em grandes bases de dados.
        Use scan_iter() para produção.
        """
        if not self._ensure_connection():
            return []
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Error on keys {pattern}: {e}")
            return []
    
    def scan_iter(self, match: str = None, count: int = 100) -> Iterator[str]:
        """
        Itera sobre chaves sem carregar todas na memória.
        RECOMENDADO para grandes bases de dados.
        
        Exemplo:
            for key in client.scan_iter(match="user:*", count=100):
                print(key)
        """
        if not self._ensure_connection():
            return iter([])
        try:
            return self.client.scan_iter(match=match, count=count)
        except Exception as e:
            logger.error(f"Error on scan_iter: {e}")
            return iter([])
    
    @recorded()
    def randomkey(self) -> Optional[str]:
        """Retorna uma chave aleatória do banco"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.randomkey()
        except Exception as e:
            logger.error(f"Error on randomkey: {e}")
            return None