import logging
from typing import List, Dict, Optional

logger = logging.getLogger('redis_simplify.client')

class UtilsMixin:
    """Utilitários avançados"""
    
    def mget(self, keys: List[str]) -> Dict[str, Optional[str]]:
        """Obtém múltiplas chaves de uma vez"""
        if not keys:
            return {}
        
        if not self._ensure_connection():
            return {key: None for key in keys}
        
        try:
            values = self.client.mget(keys)
            return dict(zip(keys, values))
        except Exception as e:
            logger.error(f"Error on mget {keys}: {e}")
            return {key: None for key in keys}
    
    def mset(self, mapping: Dict[str, str], expire_seconds: Optional[int] = None) -> bool:
        """Define múltiplas chaves de uma vez"""
        if not mapping:
            return True
        
        if not self._ensure_connection():
            return False
        
        try:
            if expire_seconds:
                pipe = self.pipeline()
                for key, value in mapping.items():
                    pipe.setex(key, expire_seconds, value)
                pipe.execute()
            else:
                self.client.mset(mapping)
            return True
        except Exception as e:
            logger.error(f"Error on mset: {e}")
            return False
    
    def rename_safe(self, old_key: str, new_key: str, overwrite: bool = False) -> bool:
        """Renomeia chave com verificação de segurança"""
        if not self._ensure_connection():
            return False
        
        try:
            if not overwrite and self.exists(new_key):
                logger.warning(f"Target key {new_key} already exists")
                return False
            
            self.client.rename(old_key, new_key)
            return True
        except Exception as e:
            logger.error(f"Error renaming {old_key} to {new_key}: {e}")
            return False
    
    def copy_key(self, source: str, destination: str, replace: bool = False) -> bool:
        """Copia chave de um lugar para outro"""
        if not self._ensure_connection():
            return False
        
        try:
            return self.client.copy(source, destination, replace=replace)
        except Exception as e:
            logger.error(f"Error copying {source} to {destination}: {e}")
            return False