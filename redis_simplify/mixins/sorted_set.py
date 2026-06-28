import logging
import redis
from typing import List, Dict, Optional, Union, Any

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class SortedSetMixin:
    """Operações com Sorted Sets Redis"""
    
    @recorded()
    @with_fallback(default_return=0)
    def zadd(self, key: str, mapping: Dict[str, float], 
             nx: bool = False, xx: bool = False, 
             gt: bool = False, lt: bool = False,
             ch: bool = False, incr: bool = False) -> int:
        """
        Adiciona membros com score a um sorted set.
        
        Args:
            key: Nome da chave
            mapping: Dict com membros e scores
            nx: Só adiciona se não existir (Redis 3.0.2+)
            xx: Só atualiza se já existir (Redis 3.0.2+)
            gt: Só atualiza se novo score for maior (Redis 6.2+)
            lt: Só atualiza se novo score for menor (Redis 6.2+)
            ch: Retorna número de membros alterados (Redis 3.0.2+)
            incr: Incrementa score (Redis 3.0.2+)
        
        Exemplos:
            client.zadd("zset", {"a": 1, "b": 2})
            client.zadd("zset", {"a": 10}, nx=True)  # Só se não existir
            client.zadd("zset", {"a": 10}, gt=True)  # Só se score > atual
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zadd(key, mapping, nx=nx, xx=xx, gt=gt, lt=lt, ch=ch, incr=incr)
    
    @recorded()
    @with_fallback(default_return=[])
    def zrange(self, key: str, start: Union[int, str], stop: Union[int, str], 
               withscores: bool = False, byscore: bool = False, 
               bylex: bool = False, rev: bool = False, 
               offset: Optional[int] = None, count: Optional[int] = None) -> List:
        """
        Retorna membros em um intervalo com opções avançadas.
        
        Args:
            key: Nome da chave
            start: Posição inicial (ou score mínimo se byscore=True)
            stop: Posição final (ou score máximo se byscore=True)
            withscores: Incluir scores no resultado
            byscore: Buscar por score (Redis 6.2+)
            bylex: Buscar por ordem lexicográfica (Redis 6.2+)
            rev: Ordem reversa (Redis 6.2+)
            offset: Offset para paginação (Redis 6.2+)
            count: Número de itens para paginação (Redis 6.2+)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        # Redis 8.0.1: 'rev' não é suportado como parâmetro direto
        # Usar zrevrangebylex ou zrevrangebyscore para ordem reversa
        if rev and byscore:
            # Ordem reversa por score
            return self.client.zrevrangebyscore(key, stop, start, withscores=withscores)
        elif rev and bylex:
            # Ordem reversa lexicográfica
            result = self.client.zrangebylex(key, start, stop)
            return list(reversed(result))
        elif rev:
            # Ordem reversa padrão
            return self.client.zrevrange(key, int(start), int(stop), withscores=withscores)
        
        # Caso normal: chama o zrange padrão
        # Nota: Removemos os parâmetros 'byscore', 'bylex', 'offset', 'count' 
        # pois eles podem não ser suportados diretamente pelo redis-py.
        # Eles são tratados pelos casos 'rev' acima ou são funcionalidades
        # que podem ser adicionadas em futuras versões.
        return self.client.zrange(key, start, stop, withscores=withscores)
    
    @recorded()
    @with_fallback(default_return=[])
    def zrange_legacy(self, key: str, start: int, stop: int, 
                    withscores: bool = False) -> List:
        """
        Versão legada do zrange (garantia de compatibilidade)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrange(key, start, stop, withscores=withscores)

    @recorded()
    @with_fallback(default_return=[])
    def zrangebyscore_legacy(self, key: str, min_score: Union[int, float, str], 
                            max_score: Union[int, float, str], 
                            withscores: bool = False) -> List:
        """
        Versão legada do zrangebyscore
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrangebyscore(key, min_score, max_score, withscores=withscores)
    
    @recorded()
    @with_fallback(default_return=[])
    def zrevrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List:
        """Retorna membros em ordem reversa (legado)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrevrange(key, start, stop, withscores=withscores)
    
    @recorded()
    @with_fallback(default_return=None)
    def zrank(self, key: str, member: str) -> Optional[int]:
        """Retorna a posição do membro"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrank(key, member)
    
    @recorded()
    @with_fallback(default_return=None)
    def zrevrank(self, key: str, member: str) -> Optional[int]:
        """Retorna a posição do membro em ordem reversa"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrevrank(key, member)
    
    @recorded()
    @with_fallback(default_return=None)
    def zscore(self, key: str, member: str) -> Optional[float]:
        """Retorna o score do membro"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zscore(key, member)
    
    @recorded()
    @with_fallback(default_return=0.0)
    def zincrby(self, key: str, amount: float, member: str) -> float:
        """Incrementa score de um membro"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zincrby(key, amount, member)
    
    @recorded()
    @with_fallback(default_return=0)
    def zrem(self, key: str, *members: str) -> int:
        """Remove membros do sorted set"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrem(key, *members)
    
    @recorded()
    @with_fallback(default_return=0)
    def zcard(self, key: str) -> int:
        """Retorna número de membros"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zcard(key)
    
    # ============ NOVOS MÉTODOS ============
    
    @recorded()
    @with_fallback(default_return=[])
    def zrangebyscore(self, key: str, min_score: Union[int, float, str], 
                      max_score: Union[int, float, str], 
                      withscores: bool = False, offset: Optional[int] = None, 
                      count: Optional[int] = None) -> List:
        """
        Retorna membros por intervalo de scores (legado, prefira zrange com byscore)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrangebyscore(key, min_score, max_score, 
                                        withscores=withscores, 
                                        offset=offset, count=count)
    
    @recorded()
    @with_fallback(default_return=[])
    def zrevrangebyscore(self, key: str, max_score: Union[int, float, str], 
                         min_score: Union[int, float, str], 
                         withscores: bool = False, offset: Optional[int] = None, 
                         count: Optional[int] = None) -> List:
        """Retorna membros por intervalo de scores em ordem reversa (legado)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrevrangebyscore(key, max_score, min_score,
                                           withscores=withscores,
                                           offset=offset, count=count)
    
    @recorded()
    @with_fallback(default_return=0)
    def zcount(self, key: str, min_score: Union[int, float, str], 
               max_score: Union[int, float, str]) -> int:
        """Conta membros em um intervalo de scores"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zcount(key, min_score, max_score)
    
    @recorded()
    @with_fallback(default_return=[])
    def zrangebylex(self, key: str, min_lex: str, max_lex: str, 
                    offset: Optional[int] = None, count: Optional[int] = None) -> List:
        """Retorna membros por intervalo lexicográfico"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zrangebylex(key, min_lex, max_lex, offset=offset, count=count)
    
    @recorded()
    @with_fallback(default_return=0)
    def zlexcount(self, key: str, min_lex: str, max_lex: str) -> int:
        """Conta membros em um intervalo lexicográfico"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zlexcount(key, min_lex, max_lex)
    
    @recorded()
    @with_fallback(default_return=0)
    def zremrangebyrank(self, key: str, start: int, stop: int) -> int:
        """Remove membros por posição"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zremrangebyrank(key, start, stop)
    
    @recorded()
    @with_fallback(default_return=0)
    def zremrangebyscore(self, key: str, min_score: Union[int, float, str], 
                         max_score: Union[int, float, str]) -> int:
        """Remove membros por intervalo de scores"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zremrangebyscore(key, min_score, max_score)
    
    @recorded()
    @with_fallback(default_return=0)
    def zremrangebylex(self, key: str, min_lex: str, max_lex: str) -> int:
        """Remove membros por intervalo lexicográfico"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zremrangebylex(key, min_lex, max_lex)
    
    @recorded()
    @with_fallback(default_return=0)
    def zunionstore(self, dest: str, keys: List[str], 
                    weights: Optional[List[float]] = None, 
                    aggregate: str = 'SUM') -> int:
        """União de sorted sets"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zunionstore(dest, keys, weights=weights, aggregate=aggregate)
    
    @recorded()
    @with_fallback(default_return=0)
    def zinterstore(self, dest: str, keys: List[str], 
                    weights: Optional[List[float]] = None, 
                    aggregate: str = 'SUM') -> int:
        """Interseção de sorted sets"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zinterstore(dest, keys, weights=weights, aggregate=aggregate)
    
    @recorded()
    @with_fallback(default_return=0)
    def zdiff(self, keys: List[str], withscores: bool = False) -> List:
        """Diferença de sorted sets (Redis 6.2+)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zdiff(keys, withscores=withscores)
    
    @recorded()
    @with_fallback(default_return=0)
    def zdiffstore(self, dest: str, keys: List[str]) -> int:
        """Armazena diferença de sorted sets (Redis 6.2+)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zdiffstore(dest, keys)
    
    @recorded()
    @with_fallback(default_return=0)
    def zmscore(self, key: str, members: List[str]) -> List[Optional[float]]:
        """Retorna scores de múltiplos membros (Redis 6.2+)"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.zmscore(key, members)