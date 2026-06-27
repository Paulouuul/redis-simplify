import logging
from typing import Optional, Dict, Any
from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class AdminMixin:

    def info(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna informações detalhadas do servidor Redis.
        
        Args:
            section: Seção específica para consultar:
                    - None: Todas as seções
                    - 'server': Informações do servidor
                    - 'clients': Informações de clientes
                    - 'memory': Informações de memória
                    - 'persistence': Informações de persistência
                    - 'stats': Estatísticas gerais
                    - 'replication': Informações de replicação
                    - 'cpu': Uso de CPU
                    - 'keyspace': Estatísticas por banco de dados
                    - 'all': Todas as seções (padrão)
        
        Returns:
            Dicionário com as informações solicitadas
        
        Exemplos:
            client.info()  # Todas as informações
            client.info('memory')  # Apenas informações de memória
            client.info('stats')  # Apenas estatísticas
            client.info('keyspace')  # Apenas keyspace
        """
        if not self._ensure_connection():
            logger.error("Cannot get info: no Redis connection")
            return {}
        
        try:
            if section:
                # Garante que section é uma string válida
                valid_sections = ['server', 'clients', 'memory', 'persistence', 
                                 'stats', 'replication', 'cpu', 'keyspace', 'all']
                if section not in valid_sections:
                    logger.warning(f"Invalid section '{section}'. Using 'all'.")
                    section = 'all'
                return self.client.info(section)
            else:
                # Retorna todas as informações
                return self.client.info()
        except Exception as e:
            logger.error(f"Error getting Redis info: {e}")
            return {}
    
    def info_sections(self) -> list:
        """Retorna lista de seções disponíveis para consulta."""
        return ['server', 'clients', 'memory', 'persistence', 
            'stats', 'replication', 'cpu', 'keyspace', 'all']
        
    
    @recorded()
    def scan(self, cursor: int = 0, match: str = None, count: int = None) -> tuple:
        """Comando SCAN do Redis"""
        if not self._ensure_connection():
            return 0, []
        try:
            return self.client.scan(cursor=cursor, match=match, count=count)
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return 0, []
    
    def dbsize(self) -> int:
        """Retorna o número de chaves no banco de dados atual"""
        if not self._ensure_connection():
            return 0
        
        try:
            return self.client.dbsize()
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0
    
    def memory_usage(self, key: str, samples: int = 0) -> Optional[int]:
        """Retorna o uso de memória de uma chave específica"""
        if not self._ensure_connection():
            return None
        
        try:
            return self.client.memory_usage(key, samples=samples)
        except Exception as e:
            logger.error(f"Error getting memory usage for '{key}': {e}")
            return None
    
    def slowlog(self, count: int = 10) -> list:
        """Retorna os comandos lentos (slowlog)"""
        if not self._ensure_connection():
            return []
        
        try:
            return self.client.slowlog('get', count)
        except Exception as e:
            logger.error(f"Error getting slowlog: {e}")
            return []
    
    def client_list(self) -> list:
        """Retorna lista de clientes conectados"""
        if not self._ensure_connection():
            return []
        
        try:
            return self.client.client_list()
        except Exception as e:
            logger.error(f"Error getting client list: {e}")
            return []
    
    @recorded()
    def flushdb(self, async_mode: bool = False) -> bool:
        """Limpa o banco de dados atual"""
        if not self._ensure_connection():
            return False
        
        try:
            if async_mode:
                self.client.flushdb(asynchronous=True)
            else:
                self.client.flushdb()
            logger.info(f"Database flushed (async={async_mode})")
            return True
        except Exception as e:
            logger.error(f"Error flushing database: {e}")
            return False
    @recorded()
    def flushall(self, async_mode: bool = False) -> bool:
        """Limpa todos os bancos (CUIDADO: apenas para testes!)"""
        if not self._ensure_connection():
            return False
        try:
            if async_mode:
                self.client.flushall(asynchronous=True)
            else:
                self.client.flushall()
            logger.warning("Redis flushall executed!")
            return True
        except Exception as e:
            logger.error(f"Error on flushall: {e}")
            return False