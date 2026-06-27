import logging
import redis
from typing import Optional, Dict, Any

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class AdminMixin:

    @with_fallback(default_return={})
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
            raise redis.ConnectionError("Redis connection failed")
        
        if section:
            valid_sections = ['server', 'clients', 'memory', 'persistence', 
                             'stats', 'replication', 'cpu', 'keyspace', 'all']
            if section not in valid_sections:
                logger.warning(f"Invalid section '{section}'. Using 'all'.")
                section = 'all'
            return self.client.info(section)
        else:
            return self.client.info()
    
    @with_fallback(default_return=[])
    def info_sections(self) -> list:
        """Retorna lista de seções disponíveis para consulta."""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return ['server', 'clients', 'memory', 'persistence', 
                'stats', 'replication', 'cpu', 'keyspace', 'all']
    
    @recorded()
    @with_fallback(default_return=(0, []))
    def scan(self, cursor: int = 0, match: str = None, count: int = None) -> tuple:
        """Comando SCAN do Redis"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.scan(cursor=cursor, match=match, count=count)
    
    @with_fallback(default_return=0)
    def dbsize(self) -> int:
        """Retorna o número de chaves no banco de dados atual"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.dbsize()
    
    @with_fallback(default_return=None)
    def memory_usage(self, key: str, samples: int = 0) -> Optional[int]:
        """Retorna o uso de memória de uma chave específica"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.memory_usage(key, samples=samples)
    
    @with_fallback(default_return=[])
    def slowlog(self, count: int = 10) -> list:
        """Retorna os comandos lentos (slowlog)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.slowlog('get', count)
    
    @with_fallback(default_return=[])
    def client_list(self) -> list:
        """Retorna lista de clientes conectados"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.client_list()
    
    @recorded()
    @with_fallback(default_return=False)
    def flushdb(self, async_mode: bool = False) -> bool:
        """Limpa o banco de dados atual"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if async_mode:
            self.client.flushdb(asynchronous=True)
        else:
            self.client.flushdb()
        logger.info(f"Database flushed (async={async_mode})")
        return True
    
    @recorded()
    @with_fallback(default_return=False)
    def flushall(self, async_mode: bool = False) -> bool:
        """Limpa todos os bancos (CUIDADO: apenas para testes!)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if async_mode:
            self.client.flushall(asynchronous=True)
        else:
            self.client.flushall()
        logger.warning("Redis flushall executed!")
        return True