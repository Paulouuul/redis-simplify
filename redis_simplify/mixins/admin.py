import logging
import redis
from typing import Optional, Dict, Any, List, Union

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
                    - 'commandstats': Estatísticas de comandos (Redis 7.0+)
                    - 'errorstats': Estatísticas de erros (Redis 7.0+)
                    - 'latencystats': Estatísticas de latência (Redis 7.0+)
                    - 'all': Todas as seções (padrão)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if section:
            valid_sections = ['server', 'clients', 'memory', 'persistence', 
                             'stats', 'replication', 'cpu', 'keyspace', 
                             'commandstats', 'errorstats', 'latencystats', 'all']
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
        # Seções disponíveis no Redis 8.0+
        return ['server', 'clients', 'memory', 'persistence', 
                'stats', 'replication', 'cpu', 'keyspace', 
                'commandstats', 'errorstats', 'latencystats', 'all']
    
    @recorded()
    @with_fallback(default_return=(0, []))
    def scan(self, cursor: int = 0, match: str = None, count: int = None, 
            type: Optional[str] = None) -> tuple:
        """Comando SCAN do Redis com filtro de tipo"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        try:
            # Tenta usar SCAN com type (Redis 6.0+)
            if type is not None:
                try:
                    # Tenta usar o SCAN nativo com type
                    return self.client.scan(cursor=cursor, match=match, count=count, type=type)
                except TypeError:
                    # Fallback: filtra manualmente
                    cursor, keys = self.client.scan(cursor=cursor, match=match, count=count)
                    filtered_keys = []
                    for key in keys:
                        if self.client.type(key) == type:
                            filtered_keys.append(key)
                    return cursor, filtered_keys
            
            return self.client.scan(cursor=cursor, match=match, count=count)
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return 0, []
    
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
    def flushdb(self, async_mode: bool = False, sync_mode: bool = False) -> bool:
        """
        Limpa o banco de dados atual.
        
        Args:
            async_mode: Executa de forma assíncrona (Redis 6.2+)
            sync_mode: Executa de forma síncrona (Redis 6.2+)
        
        Nota: async_mode e sync_mode são mutuamente exclusivos.
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if async_mode and sync_mode:
            logger.warning("Both async_mode and sync_mode are True. Using async_mode.")
            sync_mode = False
        
        if async_mode:
            self.client.flushdb(asynchronous=True)
        elif sync_mode:
            self.client.flushdb(synchronous=True)
        else:
            self.client.flushdb()
        
        logger.info(f"Database flushed (async={async_mode}, sync={sync_mode})")
        return True
    
    @recorded()
    @with_fallback(default_return=False)
    def flushall(self, async_mode: bool = False, sync_mode: bool = False) -> bool:
        """
        Limpa todos os bancos (CUIDADO: apenas para testes!)
        
        Args:
            async_mode: Executa de forma assíncrona (Redis 6.2+)
            sync_mode: Executa de forma síncrona (Redis 6.2+)
        
        Nota: async_mode e sync_mode são mutuamente exclusivos.
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if async_mode and sync_mode:
            logger.warning("Both async_mode and sync_mode are True. Using async_mode.")
            sync_mode = False
        
        if async_mode:
            self.client.flushall(asynchronous=True)
        elif sync_mode:
            self.client.flushall(synchronous=True)
        else:
            self.client.flushall()
        
        logger.warning(f"Redis flushall executed! (async={async_mode}, sync={sync_mode})")
        return True
    
    # ============ NOVOS MÉTODOS ============
    
    @with_fallback(default_return={})
    def command_info(self, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna informações sobre comandos Redis (Redis 7.0+).
        
        Args:
            command: Nome do comando específico (opcional)
        
        Returns:
            Dicionário com informações do comando
        
        Exemplo:
            info = client.command_info('SET')
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if command:
            return self.client.command_info(command)
        return self.client.command_info()
    
    @with_fallback(default_return=[])
    def command_list(self, pattern: Optional[str] = None) -> List[str]:
        """
        Retorna lista de comandos disponíveis (Redis 7.0+).
        
        Args:
            pattern: Padrão para filtrar comandos (opcional)
        
        Exemplo:
            commands = client.command_list()
            set_commands = client.command_list('*SET*')
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        if pattern:
            return self.client.command_list(pattern=pattern)
        return self.client.command_list()
    
    @with_fallback(default_return={})
    def config_get(self, parameter: str) -> Dict[str, Any]:
        """
        Obtém parâmetros de configuração do Redis.
        
        Args:
            parameter: Nome do parâmetro (ex: 'maxmemory', 'timeout')
        
        Exemplo:
            maxmemory = client.config_get('maxmemory')
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.config_get(parameter)
    
    @recorded()
    @with_fallback(default_return=False)
    def config_set(self, parameter: str, value: Any) -> bool:
        """
        Define parâmetros de configuração do Redis (CUIDADO: apenas para testes!)
        
        Args:
            parameter: Nome do parâmetro
            value: Valor a ser definido
        
        Exemplo:
            client.config_set('maxmemory', '100mb')
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        self.client.config_set(parameter, value)
        logger.info(f"Config set: {parameter} = {value}")
        return True
    
    @with_fallback(default_return={})
    def config_resetstat(self) -> bool:
        """
        Reseta as estatísticas do Redis (Redis 2.8+).
        
        Exemplo:
            client.config_resetstat()
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        self.client.config_resetstat()
        logger.info("Config stats reset")
        return True
    
    @with_fallback(default_return=0)
    def lastsave(self) -> int:
        """
        Retorna o timestamp Unix do último salvamento RDB.
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.lastsave()
    
    @with_fallback(default_return=0)
    def latency(self, subcommand: str, *args) -> Union[int, List]:
        """
        Comandos de latência (Redis 7.0+).
        
        Args:
            subcommand: 'latest', 'history', 'reset', 'graph'
            *args: Argumentos adicionais
        
        Exemplos:
            latest = client.latency('latest')
            client.latency('reset')
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.latency(subcommand, *args)
    
    @with_fallback(default_return=0)
    def time(self) -> tuple:
        """
        Retorna o tempo atual do servidor Redis.
        
        Returns:
            tuple: (timestamp_unix, microssegundos)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.time()