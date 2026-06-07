
import threading
import time

class TestRedisClientString:
    """Testes básicos de funcionalidade"""
    
    def test_set_and_get(self, client):
        """Testa set e get de strings"""
        client.set("test:key", "hello")
        assert client.get("test:key") == "hello"
        client.delete("test:key")
    
    def test_set_with_expire(self, client):
        """Testa set com expiração"""
        import time
        client.set("test:expire", "value", expire_seconds=1)
        assert client.get("test:expire") == "value"
        time.sleep(1.1)
        assert client.get("test:expire") is None
    
    def test_delete(self, client):
        """Testa delete"""
        client.set("test:delete", "value")
        assert client.exists("test:delete") is True
        client.delete("test:delete")
        assert client.exists("test:delete") is False
    
    def test_exists(self, client):
        """Testa exists"""
        client.set("test:exists", "value")
        assert client.exists("test:exists") is True
        client.delete("test:exists")
        assert client.exists("test:exists") is False
    
    def test_incr_and_decr(self, client):
        """Testa incremento e decremento"""
        client.set("test:counter", 10)
        assert client.incr("test:counter") == 11
        assert client.decr("test:counter") == 10
        client.delete("test:counter")
    
    def test_expire(self, client):
        """Testa expire separadamente"""
        import time
        client.set("test:expire2", "value")
        client.expire("test:expire2", 1)
        assert client.get("test:expire2") == "value"
        time.sleep(1.1)
        assert client.get("test:expire2") is None


class TestRedisClientJSON:
    """Testes de operações com JSON"""
    
    def test_set_json_and_get_json(self, client):
        """Testa set_json e get_json"""
        data = {"name": "João", "age": 30, "active": True}
        client.set_json("test:json", data)
        result = client.get_json("test:json")
        assert result == data
        client.delete("test:json")
    
    def test_set_json_nested(self, client):
        """Testa JSON aninhado"""
        data = {
            "user": {
                "name": "Maria",
                "address": {"city": "Rio", "zip": "12345"}
            },
            "tags": ["python", "redis"]
        }
        client.set_json("test:nested", data)
        result = client.get_json("test:nested")
        assert result == data
        client.delete("test:nested")


class TestRedisClientSets:
    """Testes de operações com Sets"""
    
    def test_sadd_and_smembers(self, client):
        """Testa adicionar e listar membros do set"""
        client.sadd("test:set", "a", "b", "c")
        members = client.smembers("test:set")
        assert members == {"a", "b", "c"}
        client.delete("test:set")
    
    def test_srem(self, client):
        """Testa remover membros do set"""
        client.sadd("test:set", "a", "b", "c")
        client.srem("test:set", "b")
        members = client.smembers("test:set")
        assert members == {"a", "c"}
        client.delete("test:set")
    
    def test_sismember(self, client):
        """Testa verificar membro do set"""
        client.sadd("test:set", "a", "b")
        assert client.sismember("test:set", "a") is True
        assert client.sismember("test:set", "c") is False
        client.delete("test:set")
    
    def test_scard(self, client):
        """Testa tamanho do set"""
        client.sadd("test:set", "a", "b", "c")
        assert client.scard("test:set") == 3
        client.delete("test:set")


class TestRedisClientHashes:
    """Testes de operações com Hashes"""
    
    def test_hset_and_hget(self, client):
        """Testa definir e obter campo de hash"""
        client.hset("test:hash", "field1", "value1")
        assert client.hget("test:hash", "field1") == "value1"
        client.delete("test:hash")
    
    def test_hgetall(self, client):
        """Testa obter todo hash"""
        client.hset("test:hash", "field1", "value1")
        client.hset("test:hash", "field2", "value2")
        result = client.hgetall("test:hash")
        assert result == {"field1": "value1", "field2": "value2"}
        client.delete("test:hash")


class TestRedisClientLists:
    """Testes de operações com Lists"""
    
    def test_lpush_and_lrange(self, client):
        """Testa adicionar à esquerda e listar"""
        client.lpush("test:list", "c", "b", "a")
        result = client.lrange("test:list", 0, -1)
        assert result == ["a", "b", "c"]
        client.delete("test:list")
    
    def test_rpush(self, client):
        """Testa adicionar à direita"""
        client.rpush("test:list", "a", "b", "c")
        result = client.lrange("test:list", 0, -1)
        assert result == ["a", "b", "c"]
        client.delete("test:list")


class TestRedisClientConnection:
    """Testes de conexão e resiliência"""
    
    def test_ping(self, client):
        """Testa ping"""
        assert client.ping() is True
    
    def test_close(self, client):
        """Testa fechar conexão"""
        client.close()
        # Depois de fechar, deve reconectar automaticamente
        assert client.ping() is True
    
    def test_ensure_connection_reconnects(self, client):
        """Testa reconexão automática"""
        # Fecha conexão
        client.close()
        # A próxima operação deve reconectar
        client.set("test:reconnect", "value")
        assert client.get("test:reconnect") == "value"
        client.delete("test:reconnect")


class TestRedisClientPipeline:
    """Testes de pipeline (operações em lote)"""
    
    def test_pipeline(self, client):
        """Testa pipeline básico"""
        pipe = client.pipeline()
        pipe.set("test:p1", "v1")
        pipe.set("test:p2", "v2")
        pipe.execute()
        
        assert client.get("test:p1") == "v1"
        assert client.get("test:p2") == "v2"
        
        client.delete("test:p1", "test:p2")


class TestRedisClientScan:
    """Testes do comando SCAN"""
    
    def test_scan(self, client):
        """Testa scan para iterar chaves"""
        # Cria várias chaves
        for i in range(10):
            client.set(f"test:scan:{i}", f"value{i}")
        
        cursor, keys = client.scan(match="test:scan:*", count=5)
        assert len(keys) > 0
        assert all(key.startswith("test:scan:") for key in keys)
        
        # Limpa
        for i in range(10):
            client.delete(f"test:scan:{i}")


class TestRedisClientSortedSet:
    """Testes de Sorted Sets (ZSET)"""
    
    def test_zadd_and_zrange(self, client):
        """Testa adicionar e listar sorted set"""
        client.zadd("test:zset", {"joao": 100, "maria": 200, "jose": 150})
        result = client.zrange("test:zset", 0, -1, withscores=True)
        assert result == [("joao", 100.0), ("jose", 150.0), ("maria", 200.0)]
        client.delete("test:zset")
    
    def test_zrevrange(self, client):
        """Testa ordem reversa"""
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3})
        result = client.zrevrange("test:zset", 0, -1, withscores=True)
        assert result == [("c", 3.0), ("b", 2.0), ("a", 1.0)]
        client.delete("test:zset")
    
    def test_zrank(self, client):
        """Testa posição do membro"""
        client.zadd("test:zset", {"joao": 100, "maria": 200, "jose": 150})
        assert client.zrank("test:zset", "joao") == 0
        assert client.zrank("test:zset", "jose") == 1
        assert client.zrank("test:zset", "maria") == 2
        client.delete("test:zset")
    
    def test_zscore(self, client):
        """Testa score do membro"""
        client.zadd("test:zset", {"joao": 100, "maria": 200})
        assert client.zscore("test:zset", "joao") == 100.0
        assert client.zscore("test:zset", "maria") == 200.0
        client.delete("test:zset")
    
    def test_zincrby(self, client):
        """Testa incremento de score"""
        client.zadd("test:zset", {"joao": 100})
        client.zincrby("test:zset", 50, "joao")
        assert client.zscore("test:zset", "joao") == 150.0
        client.delete("test:zset")
    
    def test_zrem(self, client):
        """Testa remoção de membro"""
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3})
        client.zrem("test:zset", "b")
        result = client.zrange("test:zset", 0, -1)
        assert result == ["a", "c"]
        client.delete("test:zset")
    
    def test_zcard(self, client):
        """Testa tamanho do sorted set"""
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3})
        assert client.zcard("test:zset") == 3
        client.delete("test:zset")


class TestRedisClientCache:
    """Testes de utilitários de cache"""
    
    def test_get_or_set(self, client):
        """Testa get_or_set"""
        # Primeira vez - executa função
        called = 0
        def expensive_func():
            nonlocal called
            called += 1
            return "cached_value"
        
        result1 = client.get_or_set("test:cache", expensive_func, ttl=10)
        result2 = client.get_or_set("test:cache", expensive_func, ttl=10)
        
        assert result1 == "cached_value"
        assert result2 == "cached_value"
        assert called == 1  # Função chamada apenas uma vez
        client.delete("test:cache")
    
    def test_get_or_set_json(self, client):
        """Testa get_or_set_json"""
        called = 0
        def expensive_func():
            nonlocal called
            called += 1
            return {"name": "João", "age": 30}
        
        result1 = client.get_or_set_json("test:cache_json", expensive_func, ttl=10)
        result2 = client.get_or_set_json("test:cache_json", expensive_func, ttl=10)
        
        assert result1 == {"name": "João", "age": 30}
        assert result2 == {"name": "João", "age": 30}
        assert called == 1
        client.delete("test:cache_json")
    
    def test_delete_pattern(self, client):
        """Testa delete_pattern"""
        client.set("test:pattern:1", "a")
        client.set("test:pattern:2", "b")
        client.set("test:pattern:3", "c")
        client.set("other:key", "x")
        
        deleted = client.delete_pattern("test:pattern:*")
        
        assert deleted == 3
        assert client.exists("test:pattern:1") is False
        assert client.exists("test:pattern:2") is False
        assert client.exists("test:pattern:3") is False
        assert client.exists("other:key") is True
        
        client.delete("other:key")
    
    def test_scan_iter(self, client):
        """Testa scan_iter"""
        for i in range(10):
            client.set(f"test:iter:{i}", f"value{i}")
        
        keys = list(client.scan_iter(match="test:iter:*", count=3))
        assert len(keys) == 10
        assert all(key.startswith("test:iter:") for key in keys)
        
        for i in range(10):
            client.delete(f"test:iter:{i}")


class TestRedisClientRateLimit:
    """Testes de rate limiting"""
    
    def test_rate_limit_check(self, client):
        """Testa verificação de rate limit"""
        key = "test:ratelimit"
        
        # Deve permitir as primeiras 3 requisições
        for i in range(3):
            assert client.rate_limit_check(key, 3, 60) is True
        
        # A quarta deve ser bloqueada
        assert client.rate_limit_check(key, 3, 60) is False
    
    def test_rate_limit_remaining(self, client):
        """Testa contagem de requisições restantes"""
        key = "test:remaining"
        
        assert client.rate_limit_remaining(key, 5, 60) == 5
        
        client.rate_limit_check(key, 5, 60)
        assert client.rate_limit_remaining(key, 5, 60) == 4
        
        for i in range(3):
            client.rate_limit_check(key, 5, 60)
        
        assert client.rate_limit_remaining(key, 5, 60) == 1
    
    def test_rate_limit_reset(self, client):
        """Testa tempo até reset"""
        key = "test:reset"
        reset_time = client.rate_limit_reset(key, 60)
        assert 0 <= reset_time <= 60



class TestRedisClientLock:
    """Testes de lock distribuído"""
    
    def test_lock_basic(self, client):
        """Testa lock básico"""
        with client.lock("test:lock", timeout=5):
            # Dentro do lock
            assert client.get("lock:test:lock") is not None
        
        # Lock deve ter sido liberado
        assert client.get("lock:test:lock") is None
    
    def test_lock_blocking(self, client):
        """Testa lock com blocking"""
        import threading
        import time
        
        acquired = [0]
        
        def acquire_lock():
            with client.lock("test:blocking", timeout=5, blocking_timeout=2):
                acquired[0] += 1
                time.sleep(1)
        
        t1 = threading.Thread(target=acquire_lock)
        t2 = threading.Thread(target=acquire_lock)
        
        t1.start()
        time.sleep(0.1)
        t2.start()
        
        t1.join()
        t2.join()
        
        assert acquired[0] == 2


class TestRedisClientUtils:
    """Testes de utilitários"""
    
    def test_mget(self, client):
        """Testa mget"""
        client.set("test:mget:1", "a")
        client.set("test:mget:2", "b")
        client.set("test:mget:3", "c")
        
        result = client.mget(["test:mget:1", "test:mget:2", "test:mget:3"])
        assert result == {"test:mget:1": "a", "test:mget:2": "b", "test:mget:3": "c"}
        
        client.delete("test:mget:1", "test:mget:2", "test:mget:3")
    
    def test_mset(self, client):
        """Testa mset"""
        mapping = {"test:mset:1": "a", "test:mset:2": "b", "test:mset:3": "c"}
        client.mset(mapping)
        
        assert client.get("test:mset:1") == "a"
        assert client.get("test:mset:2") == "b"
        assert client.get("test:mset:3") == "c"
        
        client.delete("test:mset:1", "test:mset:2", "test:mset:3")
    
    def test_rename_safe(self, client):
        """Testa rename seguro"""
        client.set("test:old", "value")
        
        # Renomear com overwrite=False (padrão)
        assert client.rename_safe("test:old", "test:new") is True
        assert client.exists("test:old") is False
        assert client.get("test:new") == "value"
        
        client.delete("test:new")
    
    def test_copy_key(self, client):
        """Testa cópia de chave"""
        client.set("test:source", "value")
        assert client.copy_key("test:source", "test:dest") is True
        assert client.get("test:source") == "value"
        assert client.get("test:dest") == "value"
        
        client.delete("test:source", "test:dest")

class TestRedisClientBatch:
    """Testes de operações em lote"""
    
    def test_batch_get(self, client):
        """Testa batch_get"""
        client.set("test:batch:1", "a")
        client.set("test:batch:2", "b")
        client.set("test:batch:3", "c")
        
        result = client.batch_get(["test:batch:1", "test:batch:2", "test:batch:3"])
        assert result == ["a", "b", "c"]
        
        client.delete("test:batch:1", "test:batch:2", "test:batch:3")
    
    def test_batch_set(self, client):
        """Testa batch_set"""
        items = [("test:batch:a", "1"), ("test:batch:b", "2"), ("test:batch:c", "3")]
        assert client.batch_set(items) is True
        
        assert client.get("test:batch:a") == "1"
        assert client.get("test:batch:b") == "2"
        assert client.get("test:batch:c") == "3"
        
        client.delete("test:batch:a", "test:batch:b", "test:batch:c")
    
    def test_batch_delete(self, client):
        """Testa batch_delete"""
        client.set("test:batch:d", "1")
        client.set("test:batch:e", "2")
        
        deleted = client.batch_delete(["test:batch:d", "test:batch:e"])
        assert deleted == 2
        assert client.exists("test:batch:d") is False
        assert client.exists("test:batch:e") is False



class TestRedisClientHealth:
    """Testes de health check"""
    
    def test_health_check(self, client):
        """Testa health check"""
        health = client.health_check()
        assert health["status"] == "healthy"
        assert "redis_version" in health
        assert "connected_clients" in health
    
    def test_ping_latency(self, client):
        """Testa medição de latência"""
        latency = client.ping_latency(count=5)
        assert "min_ms" in latency
        assert "max_ms" in latency
        assert "avg_ms" in latency
        assert latency["sample_count"] == 5
        assert latency["min_ms"] >= 0


class TestRedisClientDecorators:
    """Testes de decorators"""
    
    def test_cached_decorator(self, client):
        """Testa @cached decorator"""
        call_count = 0
        
        @client.cached(ttl=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        assert expensive_function(5) == 10
        assert expensive_function(5) == 10
        assert call_count == 1  # Chamada apenas uma vez (cache)
    
    def test_retry_decorator(self, client):
        """Testa @retry decorator"""
        attempt = 0
        
        @client.retry(max_attempts=3, delay=0.1)
        def unstable_function():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise Exception("Fake error")
            return "success"
        
        assert unstable_function() == "success"
        assert attempt == 2  # Tentou duas vezes


class TestRedisClientMetrics:
    """Testes de métricas de performance"""
    
    def test_enable_metrics(self, client):
        client.enable_metrics()  # ← PRIMEIRO habilita
        client.set("test", "value")  # ← DEPOIS executa
        client.get("test")
        metrics = client.get_metrics()
        assert metrics["enabled"] is True
        assert "set" in metrics["commands"]  # ← deve ter métrica do set
        assert "get" in metrics["commands"]  # ← deve ter métrica do get
    
    def test_get_metrics(self, client):
        """Testa coleta de métricas"""
        client.enable_metrics()
        
        # Executa alguns comandos
        client.set("test:metric:1", "value")
        client.get("test:metric:1")
        client.delete("test:metric:1")
        
        metrics = client.get_metrics()
        assert "commands" in metrics
        assert len(metrics["commands"]) > 0
        
        client.disable_metrics()
        client.reset_metrics()
    
    def test_reset_metrics(self, client):
        """Testa reset de métricas"""
        client.enable_metrics()
        client.set("test:reset", "value")
        client.reset_metrics()
        
        metrics = client.get_metrics()
        assert len(metrics["commands"]) == 0
        
        client.disable_metrics()
class TestRedisClientPubSub:
    """Testes de Pub/Sub"""
    
    def test_publish(self, client):
        """Testa publicação de mensagem"""
        result = client.publish("test:channel", "hello")
        assert result >= 0  # Número de subscribers
    
    def test_publish_json(self, client):
        """Testa publicação de JSON"""
        data = {"message": "hello", "user": "joao"}
        result = client.publish_json("test:channel", data)
        assert result >= 0
    
    def test_subscribe(self, client):
        """Testa inscrição em canal"""
        received = []
        
        def callback(channel, message):
            received.append((channel, message))
        
        # Subscribe em thread separada
        pubsub = client.subscribe("test:sub", callback)
        time.sleep(0.1)  # Aguarda inscrição
        
        # Publica mensagem
        client.publish("test:sub", "test message")
        time.sleep(0.1)  # Aguarda processamento
        
        assert len(received) > 0
        assert received[0][1] == "test message"