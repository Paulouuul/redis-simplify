import json
import logging
import redis
from typing import Optional, Any, Union

from redis_simplify.mixins.decorators import with_fallback
from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class JSONMixin:
    
    # ============ MÉTODOS DE DETECÇÃO ============
    
    def _has_json_module(self) -> bool:
        """Verifica se o módulo RedisJSON está disponível"""
        try:
            return hasattr(self.client, 'json')
        except:
            return False
    
    def _use_json_native(self) -> bool:
        """Determina se deve usar RedisJSON nativo ou fallback manual"""
        return self._has_json_module()
    
    def _unwrap_json_result(self, result: Any) -> Any:
        """
        Desempacota o resultado do RedisJSON.
        
        O RedisJSON sempre retorna uma lista quando você usa um path.
        Para valores únicos, extrai o primeiro item da lista.
        """
        if result is None:
            return None
        if isinstance(result, list):
            if len(result) == 1:
                value = result[0]
                # Se for uma string que parece JSON, tenta desserializar
                if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                    try:
                        return json.loads(value)
                    except:
                        return value
                return value
            if len(result) == 0:
                return None
        # Se for uma string que parece JSON, tenta desserializar
        if isinstance(result, str) and result.startswith('"') and result.endswith('"'):
            try:
                return json.loads(result)
            except:
                return result
        return result
    
    # ============ MÉTODOS BÁSICOS ============
    
    @recorded()
    @with_fallback(default_return=False)
    def set_json(self, key: str, data: Union[dict, list, Any], 
                expire_seconds: Optional[int] = None, 
                path: str = '$') -> bool:
        """
        Armazena dados JSON usando RedisJSON ou fallback manual.
        
        Args:
            key: Nome da chave
            data: Dados a serem armazenados
            expire_seconds: Tempo de expiração (opcional)
            path: Caminho JSON (padrão: '$')
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        # Se não tiver RedisJSON, usa fallback manual
        if not self._use_json_native():
            try:
                return self.set(key, json.dumps(data), expire_seconds)
            except Exception as e:
                logger.error(f"Error setting JSON fallback for {key}: {e}")
                return False
        
        try:
            self.client.json().set(key, path, data)
            if expire_seconds:
                self.client.expire(key, expire_seconds)
            return True
        except Exception as e:
            logger.error(f"Error setting JSON for {key}: {e}")
            # Fallback manual em caso de erro
            try:
                return self.set(key, json.dumps(data), expire_seconds)
            except:
                return False
    
    @recorded()
    @with_fallback(default_return=None)
    def get_json(self, key: str, path: str = '$', unwrap: bool = True) -> Optional[Any]:
        """
        Recupera dados JSON usando RedisJSON ou fallback manual.
        
        Args:
            key: Nome da chave
            path: Caminho JSON (padrão: '$')
            unwrap: Se True, desempacota resultados únicos (padrão: True)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        # Se não tiver RedisJSON, usa fallback manual
        if not self._use_json_native():
            try:
                value = self.get(key)
                return json.loads(value) if value else None
            except Exception as e:
                logger.error(f"Error getting JSON fallback for {key}: {e}")
                return None
        
        try:
            result = self.client.json().get(key, path)
            if unwrap:
                return self._unwrap_json_result(result)
            return result
        except Exception as e:
            logger.error(f"Error getting JSON for {key}: {e}")
            # Fallback manual em caso de erro
            try:
                value = self.get(key)
                return json.loads(value) if value else None
            except:
                return None
    
    # ============ MÉTODOS AVANÇADOS ============
    
    @recorded()
    @with_fallback(default_return=False)
    def set_json_path(self, key: str, path: str, value: Any) -> bool:
        """
        Define valor em um caminho JSON específico.
        
        Args:
            key: Nome da chave
            path: Caminho JSON (ex: '$.user.name')
            value: Valor a ser definido
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot set JSON path for {key}")
            return False
        
        try:
            self.client.json().set(key, path, value)
            return True
        except Exception as e:
            logger.error(f"Error setting JSON path {path} for {key}: {e}")
            return False
    
    @recorded()
    @with_fallback(default_return=None)
    def get_json_path(self, key: str, path: str = '$', unwrap: bool = True) -> Optional[Any]:
        """
        Obtém valor de um caminho JSON específico.
        
        Args:
            key: Nome da chave
            path: Caminho JSON (ex: '$.user.name')
            unwrap: Se True, desempacota resultados únicos (padrão: True)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot get JSON path for {key}")
            return None
        
        try:
            result = self.client.json().get(key, path)
            if unwrap:
                return self._unwrap_json_result(result)
            return result
        except Exception as e:
            logger.error(f"Error getting JSON path {path} for {key}: {e}")
            return None
    
    @recorded()
    @with_fallback(default_return=False)
    def delete_json(self, key: str, path: str = '$') -> bool:
        """
        Deleta um caminho JSON específico.
        
        Args:
            key: Nome da chave
            path: Caminho JSON a ser deletado (padrão: '$')
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            if path == '$':
                return bool(self.delete(key))
            logger.warning(f"RedisJSON not available, cannot delete JSON path for {key}")
            return False
        
        try:
            self.client.json().delete(key, path)
            return True
        except Exception as e:
            logger.error(f"Error deleting JSON path {path} for {key}: {e}")
            return False
    
    # ============ MÉTODOS DE ARRAY ============
    
    @recorded()
    @with_fallback(default_return=0)
    def arrappend_json(self, key: str, path: str, *values: Any) -> int:
        """
        Adiciona itens a um array JSON.
        
        Args:
            key: Nome da chave
            path: Caminho JSON para o array
            values: Valores a serem adicionados
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot append to JSON array for {key}")
            return 0
        
        try:
            result = self.client.json().arrappend(key, path, *values)
            return result if result is not None else 0
        except Exception as e:
            logger.error(f"Error appending to JSON array for {key}: {e}")
            return 0
    
    @recorded()
    @with_fallback(default_return=0)
    def arrlen_json(self, key: str, path: str = '$') -> int:
        """
        Retorna o tamanho de um array JSON.
        
        Args:
            key: Nome da chave
            path: Caminho JSON para o array
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot get array length for {key}")
            return 0
        
        try:
            result = self.client.json().arrlen(key, path)
            return self._unwrap_json_result(result) if result is not None else 0
        except Exception as e:
            logger.error(f"Error getting JSON array length for {key}: {e}")
            return 0
    
    @recorded()
    @with_fallback(default_return=0)
    def arrpop_json(self, key: str, path: str = '$', index: int = -1) -> Optional[Any]:
        """
        Remove e retorna um item de um array JSON.
        
        Args:
            key: Nome da chave
            path: Caminho JSON para o array
            index: Índice do item a remover (padrão: -1)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot pop from JSON array for {key}")
            return None
        
        try:
            result = self.client.json().arrpop(key, path, index)
            return self._unwrap_json_result(result)
        except Exception as e:
            logger.error(f"Error popping from JSON array for {key}: {e}")
            return None
    
    @recorded()
    @with_fallback(default_return=False)
    def clear_json(self, key: str, path: str = '$') -> bool:
        """
        Limpa um array ou objeto JSON.
        
        Args:
            key: Nome da chave
            path: Caminho JSON a ser limpo
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot clear JSON for {key}")
            return False
        
        try:
            self.client.json().clear(key, path)
            return True
        except Exception as e:
            logger.error(f"Error clearing JSON for {key}: {e}")
            return False
    
    # ============ MÉTODOS DE TIPO ============
    
    @recorded()
    @with_fallback(default_return=False)
    def type_json(self, key: str, path: str = '$') -> Optional[str]:
        """
        Retorna o tipo JSON de um caminho.
        
        Args:
            key: Nome da chave
            path: Caminho JSON
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot get JSON type for {key}")
            return None
        
        try:
            result = self.client.json().type(key, path)
            return self._unwrap_json_result(result) if result is not None else None
        except Exception as e:
            logger.error(f"Error getting JSON type for {key}: {e}")
            return None
    
    # ============ MÉTODOS DE MÚLTIPLAS CHAVES ============
    
    @recorded()
    @with_fallback(default_return={})
    def mget_json(self, keys: list, path: str = '$', unwrap: bool = True) -> dict:
        """
        Obtém valores JSON de múltiplas chaves.
        
        Args:
            keys: Lista de chaves
            path: Caminho JSON
            unwrap: Se True, desempacota resultados únicos (padrão: True)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if not self._use_json_native():
            logger.warning(f"RedisJSON not available, cannot get multiple JSON values")
            return {}
        
        try:
            result = {}
            for key in keys:
                value = self.client.json().get(key, path)
                if unwrap:
                    result[key] = self._unwrap_json_result(value)
                else:
                    result[key] = value
            return result
        except Exception as e:
            logger.error(f"Error getting JSON mget: {e}")
            return {}