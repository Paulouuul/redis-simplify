import logging
from typing import Optional

logger = logging.getLogger('redis_simplify.client')

class StringMixin:
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
            logger.error(f"Set {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Obtém valor de uma chave"""
        if not self._ensure_connection():
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Error on get {key}: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """Deleta uma ou mais chaves"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Error on delete {keys}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self._ensure_connection():
            return False
        try:
            result = self.client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error on exists {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Define tempo de expiração"""
        if not self._ensure_connection():
            return False
        try:
            result = self.client.expire(key, seconds)
            return bool(result)
        except Exception as e:
            logger.error(f"Error on expire {key}: {e}")
            return False
    
    def incr(self, key: str) -> int:
        """Incrementa contador"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.incr(key)
        except Exception as e:
            logger.error(f"Error on incr {key}: {e}")
            return 0
        
    def decr(self, key: str) -> int:
        """Decrementa contador"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.decr(key)
        except Exception as e:
            logger.error(f"Error on decr {key}: {e}")
            return 0