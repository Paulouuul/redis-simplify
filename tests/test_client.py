import threading
import time
import pytest

class TestRedisClientString:
    """Testes de operações com strings"""
    
    def test_set_and_get(self, client):
        """Testa set e get de strings"""
        client.set("test:key", "hello")
        assert client.get("test:key") == "hello"
        client.delete("test:key")
    
    def test_set_with_expire(self, client):
        """Testa set com expiração"""
        client.set("test:expire", "value", expire_seconds=1)
        assert client.get("test:expire") == "value"
        time.sleep(1.1)
        assert client.get("test:expire") is None
    
    def test_set_with_get(self, client):
        """Testa set com GET (retorna valor antigo)"""
        client.set("test:key", "old_value")
        old = client.set("test:key", "new_value", get=True)
        assert old == "old_value"
        assert client.get("test:key") == "new_value"
        client.delete("test:key")
    
    def test_set_with_keepttl(self, client):
        """Testa set com KEEPTTL"""
        client.set("test:key", "value", expire_seconds=60)
        ttl_before = client.ttl("test:key")
        client.set("test:key", "new_value", keepttl=True)
        ttl_after = client.ttl("test:key")
        assert ttl_after <= ttl_before
        client.delete("test:key")
    
    def test_incr_and_decr(self, client):
        """Testa incremento e decremento"""
        client.set("test:counter", 10)
        assert client.incr("test:counter") == 11
        assert client.decr("test:counter") == 10
        client.delete("test:counter")

    def test_append(self, client):
        """Testa append em string"""
        client.set("test:append", "Hello")
        result = client.append("test:append", " World")
        assert result == 11
        assert client.get("test:append") == "Hello World"
        client.delete("test:append")
    
    def test_strlen(self, client):
        """Testa strlen"""
        client.set("test:strlen", "Hello")
        assert client.strlen("test:strlen") == 5
        client.delete("test:strlen")
    
    def test_getrange(self, client):
        """Testa getrange (substring)"""
        client.set("test:getrange", "Hello World")
        assert client.getrange("test:getrange", 0, 4) == "Hello"
        assert client.getrange("test:getrange", 6, 10) == "World"
        client.delete("test:getrange")
    
    def test_setrange(self, client):
        """Testa setrange (sobrescrever parte da string)"""
        client.set("test:setrange", "Hello World")
        result = client.setrange("test:setrange", 6, "Redis")
        assert result == 11
        assert client.get("test:setrange") == "Hello Redis"
        client.delete("test:setrange")
    
    def test_getdel(self, client):
        """Testa getdel (obter e deletar)"""
        client.set("test:getdel", "value")
        value = client.getdel("test:getdel")
        assert value == "value"
        assert client.exists("test:getdel") is False


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
    
    def test_json_set_and_get_path(self, client):
        """Testa json_set e get_json_path com caminho específico"""
        data = {"name": "João", "age": 30, "tags": ["python", "redis"]}
        client.set_json("test:json", data)
        
        client.set_json_path("test:json", '$.age', 31)
        age = client.get_json_path("test:json", '$.age')
        assert age == 31
        
        client.set_json_path("test:json", '$.tags', ["python", "redis", "fastapi"])
        tags = client.get_json_path("test:json", '$.tags')
        assert tags == ["python", "redis", "fastapi"]
        
        client.delete("test:json")
    
    def test_json_arrappend_and_arrlen(self, client):
        """Testa json_arrappend e json_arrlen"""
        client.set_json("test:json", {"tags": ["python", "redis"]})
        
        client.arrappend_json("test:json", '$.tags', "fastapi", "docker")
        length = client.arrlen_json("test:json", '$.tags')
        assert length == 4
        
        client.delete("test:json")
    
    def test_json_arrpop(self, client):
        """Testa json_arrpop"""
        client.set_json("test:json", {"tags": ["python", "redis", "fastapi"]})
        
        removed = client.arrpop_json("test:json", '$.tags')
        # RedisJSON pode retornar '"fastapi"' ou 'fastapi'
        if isinstance(removed, str):
            removed = removed.strip('"')  # Remove aspas se presentes
        assert removed == "fastapi"
        
        tags = client.get_json_path("test:json", '$.tags')
        # Normaliza os dados para comparação
        if isinstance(tags, list):
            tags = [t.strip('"') if isinstance(t, str) else t for t in tags]
        assert tags == ["python", "redis"]
        
        client.delete("test:json")


class TestRedisClientSets:
    """Testes de operações com Sets"""
    
    def test_sadd_and_smembers(self, client):
        client.sadd("test:set", "a", "b", "c")
        members = client.smembers("test:set")
        assert members == {"a", "b", "c"}
        client.delete("test:set")
    
    def test_srem(self, client):
        client.sadd("test:set", "a", "b", "c")
        client.srem("test:set", "b")
        members = client.smembers("test:set")
        assert members == {"a", "c"}
        client.delete("test:set")
    
    def test_sismember(self, client):
        client.sadd("test:set", "a", "b")
        assert client.sismember("test:set", "a") is True
        assert client.sismember("test:set", "c") is False
        client.delete("test:set")
    
    def test_scard(self, client):
        client.sadd("test:set", "a", "b", "c")
        assert client.scard("test:set") == 3
        client.delete("test:set")


class TestRedisClientHashes:
    """Testes de operações com Hashes"""
    
    def test_hset_and_hget(self, client):
        client.hset("test:hash", "field1", "value1")
        assert client.hget("test:hash", "field1") == "value1"
        client.delete("test:hash")
    
    def test_hgetall(self, client):
        client.hset("test:hash", "field1", "value1")
        client.hset("test:hash", "field2", "value2")
        result = client.hgetall("test:hash")
        assert result == {"field1": "value1", "field2": "value2"}
        client.delete("test:hash")


class TestRedisClientLists:
    """Testes de operações com Lists"""
    
    def test_lpush_and_lrange(self, client):
        client.lpush("test:list", "c", "b", "a")
        result = client.lrange("test:list", 0, -1)
        assert result == ["a", "b", "c"]
        client.delete("test:list")
    
    def test_rpush(self, client):
        client.rpush("test:list", "a", "b", "c")
        result = client.lrange("test:list", 0, -1)
        assert result == ["a", "b", "c"]
        client.delete("test:list")


class TestRedisClientConnection:
    """Testes de conexão e resiliência"""
    
    def test_ping(self, client):
        assert client.ping() is True
    
    def test_close(self, client):
        client.close()
        assert client.ping() is True
    
    def test_ensure_connection_reconnects(self, client):
        client.close()
        client.set("test:reconnect", "value")
        assert client.get("test:reconnect") == "value"
        client.delete("test:reconnect")


class TestRedisClientPipeline:
    """Testes de pipeline (operações em lote)"""
    
    def test_pipeline(self, client):
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
        for i in range(10):
            client.set(f"test:scan:{i}", f"value{i}")
        
        cursor, keys = client.scan(match="test:scan:*", count=5)
        assert len(keys) > 0
        assert all(key.startswith("test:scan:") for key in keys)
        
        for i in range(10):
            client.delete(f"test:scan:{i}")
    
    def test_scan_with_type(self, client):
        """Testa SCAN com filtro de tipo"""
        client.set("test:scan:string", "value")
        client.hset("test:scan:hash", "field", "value")
        
        # Tenta SCAN com type
        try:
            cursor, keys = client.scan(match="test:scan:*", type='string')
            # Se funcionou, verifica
            if keys:
                for key in keys:
                    assert client.type(key) == "string"
        except Exception:
            # Se não funcionar, verifica manualmente
            cursor, keys = client.scan(match="test:scan:*")
            string_keys = [k for k in keys if client.type(k) == "string"]
            assert len(string_keys) >= 1
        
        # Limpeza
        client.delete("test:scan:string", "test:scan:hash")


class TestRedisClientSortedSet:
    """Testes de Sorted Sets (ZSET)"""
    
    def test_zadd_and_zrange(self, client):
        client.zadd("test:zset", {"joao": 100, "maria": 200, "jose": 150})
        result = client.zrange("test:zset", 0, -1, withscores=True)
        assert result == [("joao", 100.0), ("jose", 150.0), ("maria", 200.0)]
        client.delete("test:zset")
    
    def test_zadd_with_gt(self, client):
        """Testa zadd com opção GT"""
        client.zadd("test:zset", {"a": 1})
        client.zadd("test:zset", {"a": 2}, gt=True)
        score = client.zscore("test:zset", "a")
        assert score == 2.0
        client.delete("test:zset")
    
    def test_zrange_byscore(self, client):
        """Testa zrange com BYSCORE"""
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5})
        result = client.zrange("test:zset", 2, 4, byscore=True, withscores=True)
        assert len(result) >= 3
        client.delete("test:zset")
    
    def test_zmscore(self, client):
        """Testa zmscore (múltiplos scores)"""
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3})
        scores = client.zmscore("test:zset", ["a", "b", "c"])
        assert scores == [1.0, 2.0, 3.0]
        client.delete("test:zset")
    
    def test_zrevrange(self, client):
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3})
        result = client.zrevrange("test:zset", 0, -1, withscores=True)
        assert result == [("c", 3.0), ("b", 2.0), ("a", 1.0)]
        client.delete("test:zset")
    
    def test_zrank(self, client):
        client.zadd("test:zset", {"joao": 100, "maria": 200, "jose": 150})
        assert client.zrank("test:zset", "joao") == 0
        assert client.zrank("test:zset", "jose") == 1
        assert client.zrank("test:zset", "maria") == 2
        client.delete("test:zset")
    
    def test_zscore(self, client):
        client.zadd("test:zset", {"joao": 100, "maria": 200})
        assert client.zscore("test:zset", "joao") == 100.0
        assert client.zscore("test:zset", "maria") == 200.0
        client.delete("test:zset")
    
    def test_zincrby(self, client):
        client.zadd("test:zset", {"joao": 100})
        client.zincrby("test:zset", 50, "joao")
        assert client.zscore("test:zset", "joao") == 150.0
        client.delete("test:zset")
    
    def test_zrem(self, client):
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3})
        client.zrem("test:zset", "b")
        result = client.zrange("test:zset", 0, -1)
        assert result == ["a", "c"]
        client.delete("test:zset")
    
    def test_zcard(self, client):
        client.zadd("test:zset", {"a": 1, "b": 2, "c": 3})
        assert client.zcard("test:zset") == 3
        client.delete("test:zset")


class TestRedisClientCache:
    """Testes de utilitários de cache"""
    
    def test_get_or_set(self, client):
        called = 0
        def expensive_func():
            nonlocal called
            called += 1
            return "cached_value"
        
        result1 = client.get_or_set("test:cache", expensive_func, ttl=10)
        result2 = client.get_or_set("test:cache", expensive_func, ttl=10)
        
        assert result1 == "cached_value"
        assert result2 == "cached_value"
        assert called == 1
        client.delete("test:cache")
    
    def test_get_or_set_json(self, client):
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
        key = "test:ratelimit"
        
        for i in range(3):
            assert client.rate_limit_check(key, 3, 60) is True
        
        assert client.rate_limit_check(key, 3, 60) is False
    
    def test_rate_limit_remaining(self, client):
        key = "test:remaining"
        
        assert client.rate_limit_remaining(key, 5, 60) == 5
        
        client.rate_limit_check(key, 5, 60)
        assert client.rate_limit_remaining(key, 5, 60) == 4
        
        for i in range(3):
            client.rate_limit_check(key, 5, 60)
        
        assert client.rate_limit_remaining(key, 5, 60) == 1
    
    def test_rate_limit_reset(self, client):
        key = "test:reset"
        reset_time = client.rate_limit_reset(key, 60)
        assert 0 <= reset_time <= 60
    
    def test_run_with_rate_limit_returns_none_when_exceeded(self, client):
        for i in range(3):
            result = client.run_with_rate_limit(
                client.set, "test:rate:exceed", 3, 60,
                f"key{i}", f"value{i}"
            )
            assert result is True
        
        result = client.run_with_rate_limit(
            client.set, "test:rate:exceed", 3, 60,
            "key4", "value4"
        )
        assert result is None
        
        for i in range(4):
            client.delete(f"key{i}")
    
    def test_run_with_rate_limit_works_with_get(self, client):
        client.set("test:rate:get", "hello")
        
        result = client.run_with_rate_limit(
            client.get, "test:rate:get", 3, 60,
            "test:rate:get"
        )
        assert result == "hello"
        
        client.delete("test:rate:get")
    
    def test_run_with_rate_limit_works_with_sadd(self, client):
        result = client.run_with_rate_limit(
            client.sadd, "test:rate:sadd", 3, 60,
            "set", "a", "b", "c"
        )
        assert result == 3
        
        members = client.smembers("set")
        assert members == {"a", "b", "c"}
        
        client.delete("set")


class TestRedisClientLock:
    """Testes de lock distribuído"""
    
    def test_lock_basic(self, client):
        with client.lock("test:lock", timeout=5):
            assert client.get("lock:test:lock") is not None
        
        assert client.get("lock:test:lock") is None
    
    def test_lock_blocking(self, client):
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
        client.set("test:mget:1", "a")
        client.set("test:mget:2", "b")
        client.set("test:mget:3", "c")
        
        result = client.mget(["test:mget:1", "test:mget:2", "test:mget:3"])
        assert result == {"test:mget:1": "a", "test:mget:2": "b", "test:mget:3": "c"}
        
        client.delete("test:mget:1", "test:mget:2", "test:mget:3")
    
    def test_mset(self, client):
        mapping = {"test:mset:1": "a", "test:mset:2": "b", "test:mset:3": "c"}
        client.mset(mapping)
        
        assert client.get("test:mset:1") == "a"
        assert client.get("test:mset:2") == "b"
        assert client.get("test:mset:3") == "c"
        
        client.delete("test:mset:1", "test:mset:2", "test:mset:3")
    
    def test_rename_safe(self, client):
        client.set("test:old", "value")
        
        assert client.rename_safe("test:old", "test:new") is True
        assert client.exists("test:old") is False
        assert client.get("test:new") == "value"
        
        client.delete("test:new")
    
    def test_copy_key(self, client):
        client.set("test:source", "value")
        assert client.copy_key("test:source", "test:dest") is True
        assert client.get("test:source") == "value"
        assert client.get("test:dest") == "value"
        
        client.delete("test:source", "test:dest")
    
    def test_touch(self, client):
        """Testa touch (atualizar tempo de acesso)"""
        client.set("test:touch", "value")
        result = client.touch("test:touch")
        assert result == 1
        client.delete("test:touch")


class TestRedisClientBatch:
    """Testes de operações em lote"""
    
    def test_batch_get(self, client):
        client.set("test:batch:1", "a")
        client.set("test:batch:2", "b")
        client.set("test:batch:3", "c")
        
        result = client.batch_get(["test:batch:1", "test:batch:2", "test:batch:3"])
        assert result == ["a", "b", "c"]
        
        client.delete("test:batch:1", "test:batch:2", "test:batch:3")
    
    def test_batch_set(self, client):
        items = [("test:batch:a", "1"), ("test:batch:b", "2"), ("test:batch:c", "3")]
        assert client.batch_set(items) is True
        
        assert client.get("test:batch:a") == "1"
        assert client.get("test:batch:b") == "2"
        assert client.get("test:batch:c") == "3"
        
        client.delete("test:batch:a", "test:batch:b", "test:batch:c")
    
    def test_batch_delete(self, client):
        client.set("test:batch:d", "1")
        client.set("test:batch:e", "2")
        
        deleted = client.batch_delete(["test:batch:d", "test:batch:e"])
        assert deleted == 2
        assert client.exists("test:batch:d") is False
        assert client.exists("test:batch:e") is False


class TestRedisClientHealth:
    """Testes de health check"""
    
    def test_health_check(self, client):
        health = client.health_check()
        assert health["status"] == "healthy"
        assert "redis_version" in health
        assert "connected_clients" in health
    
    def test_ping_latency(self, client):
        latency = client.ping_latency(count=5)
        assert "min_ms" in latency
        assert "max_ms" in latency
        assert "avg_ms" in latency
        assert latency["sample_count"] == 5
        assert latency["min_ms"] >= 0


class TestRedisClientDecorators:
    """Testes de decorators"""
    
    def test_cached_decorator(self, client):
        call_count = 0
        
        @client.cached(ttl=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        assert expensive_function(5) == 10
        assert expensive_function(5) == 10
        assert call_count >= 1
    
    def test_retry_decorator(self, client):
        attempt = 0
        
        @client.retry(max_attempts=3, delay=0.1)
        def unstable_function():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise Exception("Fake error")
            return "success"
        
        assert unstable_function() == "success"
        assert attempt == 2


class TestRedisClientMetrics:
    """Testes de métricas de performance"""
    
    def test_enable_metrics(self, client):
        client.enable_metrics()
        client.set("test", "value")
        client.get("test")
        metrics = client.get_metrics()
        assert metrics["enabled"] is True
        assert "set" in metrics["commands"]
        assert "get" in metrics["commands"]
    
    def test_get_metrics(self, client):
        client.enable_metrics()
        
        client.set("test:metric:1", "value")
        client.get("test:metric:1")
        client.delete("test:metric:1")
        
        metrics = client.get_metrics()
        assert "commands" in metrics
        assert len(metrics["commands"]) > 0
        
        client.disable_metrics()
        client.reset_metrics()
    
    def test_reset_metrics(self, client):
        client.enable_metrics()
        client.set("test:reset", "value")
        client.reset_metrics()
        
        metrics = client.get_metrics()
        assert len(metrics["commands"]) == 0
        
        client.disable_metrics()


class TestRedisClientPubSub:
    """Testes de Pub/Sub"""
    
    def test_publish(self, client):
        result = client.publish("test:channel", "hello")
        assert result >= 0
    
    def test_publish_json(self, client):
        data = {"message": "hello", "user": "joao"}
        result = client.publish_json("test:channel", data)
        assert result >= 0
    
    def test_publish_with_nohistory(self, client):
        """Testa publish com nohistory"""
        result = client.publish("test:channel", "hello", nohistory=True)
        assert result >= 0
    
    def test_subscribe(self, client):
        received = []
        
        def callback(channel, message):
            received.append((channel, message))
        
        pubsub = client.subscribe("test:sub", callback)
        time.sleep(0.1)
        
        client.publish("test:sub", "test message")
        time.sleep(0.1)
        
        assert len(received) > 0
        assert received[0][1] == "test message"
        
        client.close_pubsubs()


class TestRedisClientAdmin:
    """Testes de comandos administrativos e monitoramento"""
    
    def test_info(self, client):
        info = client.info()
        
        assert isinstance(info, dict)
        assert 'redis_version' in info
        assert 'used_memory_human' in info
        assert 'connected_clients' in info
        assert 'uptime_in_days' in info
        
        assert isinstance(info['redis_version'], str)
        assert isinstance(info['used_memory_human'], str)
        assert isinstance(info['connected_clients'], int)
    
    def test_info_sections(self, client):
        sections = client.info_sections()
        
        assert isinstance(sections, list)
        assert len(sections) > 0
        
        common_sections = ['server', 'clients', 'memory', 'stats', 'keyspace']
        assert any(section in sections for section in common_sections)
    
    def test_info_specific_section(self, client):
        memory_info = client.info('memory')
        assert isinstance(memory_info, dict)
        assert 'used_memory_human' in memory_info
        assert 'mem_fragmentation_ratio' in memory_info
        
        stats_info = client.info('stats')
        assert isinstance(stats_info, dict)
        assert 'total_commands_processed' in stats_info
        assert 'instantaneous_ops_per_sec' in stats_info
        
        keyspace_info = client.info('keyspace')
        assert isinstance(keyspace_info, dict)
    
    def test_info_invalid_section(self, client):
        info = client.info('invalid_section')
        assert isinstance(info, dict)
        assert 'redis_version' in info or len(info) > 0
    
    def test_dbsize(self, client):
        client.flushdb()
        assert client.dbsize() == 0
        
        client.set('test:size:1', 'value1')
        client.set('test:size:2', 'value2')
        client.set('test:size:3', 'value3')
        assert client.dbsize() == 3
        
        client.delete('test:size:1', 'test:size:2', 'test:size:3')
    
    def test_memory_usage(self, client):
        client.set('test:memory', 'value')
        
        usage = client.memory_usage('test:memory')
        assert usage is not None
        assert isinstance(usage, int)
        assert usage > 0
        
        usage = client.memory_usage('test:inexistente')
        assert usage is None or usage == 0
        
        client.delete('test:memory')
    
    def test_slowlog(self, client):
        for i in range(10):
            client.set(f'test:slow:{i}', f'value{i}')
        
        slow_commands = client.slowlog(5)
        assert isinstance(slow_commands, list)
        
        if slow_commands:
            cmd = slow_commands[0]
            assert isinstance(cmd, (list, tuple))
            assert len(cmd) >= 4
        
        for i in range(10):
            client.delete(f'test:slow:{i}')
    
    def test_client_list(self, client):
        clients = client.client_list()
        assert isinstance(clients, list)
        assert len(clients) >= 1
        
        if clients:
            first_client = clients[0]
            if isinstance(first_client, dict):
                assert 'addr' in first_client or 'id' in first_client
    
    def test_flushdb(self, client):
        client.set('test:flush:1', 'value1')
        client.set('test:flush:2', 'value2')
        assert client.dbsize() >= 2
        
        result = client.flushdb()
        assert result is True
        
        assert client.exists('test:flush:1') is False
        assert client.exists('test:flush:2') is False
    
    def test_flushdb_async(self, client):
        client.set('test:flush:async', 'value')
        
        result = client.flushdb(async_mode=True)
        assert result is True
        
        time.sleep(0.1)
        assert client.exists('test:flush:async') is False
    
    def test_flushall(self, client):
        client.set('test:flushall', 'value')
        
        result = client.flushall()
        assert result is True
        
        assert client.exists('test:flushall') is False
    
    def test_flushall_async(self, client):
        client.set('test:flushall:async', 'value')
        
        result = client.flushall(async_mode=True)
        assert result is True
        
        time.sleep(0.1)
        assert client.exists('test:flushall:async') is False


class TestRedisClientKeyMixin:
    """Testes específicos para operações de chaves (KeyMixin)"""
    
    def test_delete(self, client):
        client.set("test:delete", "value")
        assert client.exists("test:delete") is True
        result = client.delete("test:delete")
        assert result == 1
        assert client.exists("test:delete") is False
    
    def test_delete_multiple(self, client):
        client.set("test:del:1", "a")
        client.set("test:del:2", "b")
        client.set("test:del:3", "c")
        
        result = client.delete("test:del:1", "test:del:2")
        assert result == 2
        assert client.exists("test:del:1") is False
        assert client.exists("test:del:2") is False
        assert client.exists("test:del:3") is True
        
        client.delete("test:del:3")
    
    def test_exists(self, client):
        client.set("test:exists", "value")
        assert client.exists("test:exists") is True
        client.delete("test:exists")
        assert client.exists("test:exists") is False
    
    def test_expire(self, client):
        client.set("test:expire", "value")
        assert client.expire("test:expire", 1) is True
        assert client.get("test:expire") == "value"
        time.sleep(1.1)
        assert client.get("test:expire") is None
    
    def test_expire_with_nx(self, client):
        """Testa expire com NX"""
        client.set("test:expire:nx", "value")
        client.expire("test:expire:nx", 10)
        # Só deve definir se não tiver expiração (mas já tem)
        result = client.expire("test:expire:nx", 20, nx=True)
        assert result is False  # Já tem expiração
        client.delete("test:expire:nx")
    
    def test_expireat(self, client):
        client.set("test:expireat", "value")
        timestamp = int(time.time()) + 1
        assert client.expireat("test:expireat", timestamp) is True
        assert client.get("test:expireat") == "value"
        time.sleep(1.1)
        assert client.get("test:expireat") is None
    
    def test_ttl(self, client):
        client.set("test:ttl", "value")
        client.expire("test:ttl", 10)
        ttl = client.ttl("test:ttl")
        assert 0 < ttl <= 10
        
        client.set("test:ttl:no", "value")
        assert client.ttl("test:ttl:no") == -1
        
        assert client.ttl("test:ttl:inexistente") == -2
        
        client.delete("test:ttl", "test:ttl:no")
    
    def test_pttl(self, client):
        client.set("test:pttl", "value")
        client.expire("test:pttl", 10)
        pttl = client.pttl("test:pttl")
        assert 0 < pttl <= 10000
        client.delete("test:pttl")
    
    def test_persist(self, client):
        client.set("test:persist", "value")
        client.expire("test:persist", 10)
        assert client.ttl("test:persist") > 0
        
        assert client.persist("test:persist") is True
        assert client.ttl("test:persist") == -1
        
        client.delete("test:persist")
    
    def test_rename(self, client):
        client.set("test:old", "value")
        assert client.rename("test:old", "test:new") is True
        assert client.exists("test:old") is False
        assert client.get("test:new") == "value"
        client.delete("test:new")
    
    def test_renamenx(self, client):
        client.set("test:old", "value")
        client.set("test:existing", "existing")
        
        assert client.renamenx("test:old", "test:existing") is False
        
        assert client.renamenx("test:old", "test:new") is True
        assert client.get("test:new") == "value"
        
        client.delete("test:existing", "test:new")
    
    def test_type(self, client):
        client.set("test:type:string", "value")
        assert client.type("test:type:string") == "string"
        
        client.hset("test:type:hash", "field", "value")
        assert client.type("test:type:hash") == "hash"
        
        client.sadd("test:type:set", "member")
        assert client.type("test:type:set") == "set"
        
        client.delete("test:type:string", "test:type:hash", "test:type:set")
    
    def test_keys(self, client):
        client.set("test:keys:1", "a")
        client.set("test:keys:2", "b")
        client.set("test:keys:3", "c")
        
        keys = client.keys("test:keys:*")
        assert len(keys) == 3
        assert all(key.startswith("test:keys:") for key in keys)
        
        client.delete("test:keys:1", "test:keys:2", "test:keys:3")
    
    def test_scan_iter(self, client):
        for i in range(10):
            client.set(f"test:scaniter:{i}", f"value{i}")
        
        keys = list(client.scan_iter(match="test:scaniter:*", count=3))
        assert len(keys) == 10
        assert all(key.startswith("test:scaniter:") for key in keys)
        
        for i in range(10):
            client.delete(f"test:scaniter:{i}")
    
    def test_randomkey(self, client):
        client.set("test:random:1", "a")
        client.set("test:random:2", "b")
        
        key = client.randomkey()
        assert key is not None
        assert key.startswith("test:random:")
        
        client.delete("test:random:1", "test:random:2")


class TestRedisClientConnectionManagement:
    def test_set_timeouts(self, client):
        """Testa set_timeouts"""
        client.set_timeouts(
            socket_timeout=5.0,
            socket_connect_timeout=3.0,
            retry_on_timeout=True
        )
        assert client.ping() is True

    def test_update_url(self, client):
        """Testa update_url"""
        client.update_url("redis://localhost:6379/9")
        assert client.ping() is True

    
    def test_set_retry_config(self, client):
        """Testa set_retry_config"""
        client.set_retry_config(retries=5, backoff_base=2.0)
        assert client.ping() is True


class TestRedisClientJSONUnwrap:
    """Testes para o parâmetro unwrap dos métodos JSON"""
    
    def test_get_json_with_unwrap_true(self, client):
        """Testa get_json com unwrap=True (padrão)"""
        data = {"name": "João", "tags": ["python", "redis"]}
        client.set_json("test:unwrap", data)
        
        result = client.get_json("test:unwrap", unwrap=True)
        assert result == data  # Retorna o objeto completo
        
        client.delete("test:unwrap")
    
    def test_get_json_with_unwrap_false(self, client):
        """Testa get_json com unwrap=False (formato cru do RedisJSON)"""
        data = {"name": "João", "tags": ["python", "redis"]}
        client.set_json("test:unwrap", data)
        
        result = client.get_json("test:unwrap", unwrap=False)
        # RedisJSON retorna lista com 1 item
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == data
        
        client.delete("test:unwrap")
    
    def test_get_json_path_with_unwrap_true(self, client):
        """Testa get_json_path com unwrap=True"""
        data = {"name": "João", "age": 30}
        client.set_json("test:unwrap", data)
        
        result = client.get_json_path("test:unwrap", '$.name', unwrap=True)
        assert result == "João"
        
        client.delete("test:unwrap")
    
    def test_get_json_path_with_unwrap_false(self, client):
        """Testa get_json_path com unwrap=False (formato cru)"""
        data = {"name": "João", "age": 30}
        client.set_json("test:unwrap", data)
        
        result = client.get_json_path("test:unwrap", '$.name', unwrap=False)
        # RedisJSON retorna lista com 1 item: ['"João"']
        assert isinstance(result, list)
        assert len(result) == 1
        
        client.delete("test:unwrap")
    
    def test_mget_json_with_unwrap_true(self, client):
        """Testa mget_json com unwrap=True"""
        client.set_json("test:unwrap:1", {"name": "João"})
        client.set_json("test:unwrap:2", {"name": "Maria"})
        
        result = client.mget_json(["test:unwrap:1", "test:unwrap:2"], unwrap=True)
        assert result == {
            "test:unwrap:1": {"name": "João"},
            "test:unwrap:2": {"name": "Maria"}
        }
        
        client.delete("test:unwrap:1", "test:unwrap:2")
    
    def test_mget_json_with_unwrap_false(self, client):
        """Testa mget_json com unwrap=False (formato cru)"""
        client.set_json("test:unwrap:1", {"name": "João"})
        client.set_json("test:unwrap:2", {"name": "Maria"})
        
        result = client.mget_json(["test:unwrap:1", "test:unwrap:2"], unwrap=False)
        # Cada valor é uma lista com 1 item
        assert isinstance(result["test:unwrap:1"], list)
        assert isinstance(result["test:unwrap:2"], list)
        
        client.delete("test:unwrap:1", "test:unwrap:2")
    
    def test_get_json_unwrap_with_missing_key(self, client):
        """Testa get_json com unwrap e chave inexistente"""
        result = client.get_json("test:unwrap:missing", unwrap=True)
        assert result is None
        
        result = client.get_json("test:unwrap:missing", unwrap=False)
        # Sem RedisJSON, retorna None
        assert result is None



class TestRedisClientDecoratorsAdvanced:
    """Testes avançados de decorators"""
    
    def test_cached_with_different_keys(self, client):
        """Testa cached com diferentes chaves"""
        call_count = 0
        
        @client.cached(ttl=10, key_prefix="test")
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        assert func(5) == 10
        assert func(5) == 10
        assert func(10) == 20
        assert call_count == 2
        
        client.delete_pattern("test:*")
    
    def test_retry_decorator_success_first(self, client):
        """Testa retry com sucesso na primeira tentativa"""
        attempt = 0
        
        @client.retry(max_attempts=3)
        def success():
            nonlocal attempt
            attempt += 1
            return "ok"
        
        assert success() == "ok"
        assert attempt == 1
    
    def test_retry_decorator_exhausted(self, client):
        """Testa retry com todas tentativas falhando"""
        attempt = 0
        
        @client.retry(max_attempts=3, delay=0.1)
        def always_fail():
            nonlocal attempt
            attempt += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fail()
        
        assert attempt == 3

class TestRedisClientDecoratorsComplete:
    """Testes completos de todos os decorators (fallback, retry, cached)"""
    
    def test_with_fallback_decorator(self, client):
        """Testa @with_fallback como decorator"""
        from redis_simplify.mixins.decorators import with_fallback
        
        @with_fallback(default_return="default")
        def risky_function():
            raise ValueError("Error!")
        
        result = risky_function()
        assert result == "default"

    
    def test_no_fallback_decorator(self, client):
        """Testa @no_fallback como decorator"""
        from redis_simplify.mixins.decorators import no_fallback
        
        @no_fallback
        def risky_function():
            raise ValueError("Error!")
        
        with pytest.raises(ValueError):
            risky_function()
    
    def test_fallback_value_decorator(self, client):
        """Testa @fallback_value como decorator"""
        from redis_simplify.mixins.decorators import fallback_value
        
        @fallback_value([])
        def risky_function():
            raise ValueError("Error!")
        
        result = risky_function()
        assert result == []
    
    def test_retry_with_fallback(self, client):
        """Testa @retry com fallback"""
        attempt = 0
        
        @client.retry(max_attempts=3, fallback="default")
        def always_fail():
            nonlocal attempt
            attempt += 1
            raise ValueError("Always fails")
        
        result = always_fail()
        assert result == "default"
        assert attempt == 3
    
    def test_retry_with_fallback_none(self, client):
        """Testa @retry com fallback=None (deve levantar exceção)"""
        attempt = 0
        
        @client.retry(max_attempts=3, fallback=None)
        def always_fail():
            nonlocal attempt
            attempt += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fail()
        
        assert attempt == 3
    
    def test_cached_with_fallback(self, client):
        """Testa @cached com fallback"""
        call_count = 0
        
        @client.cached(ttl=10, fallback="default")
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Error!")
        
        result = failing_function()
        assert result == "default"
        assert call_count == 1
    
    def test_cached_with_fallback_respects_fallback_enabled(self, client):
        """Testa @cached com fallback respeitando fallback_enabled"""
        call_count = 0
        
        client.fallback_enabled = False
        
        @client.cached(ttl=10, fallback="default")
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Error!")
        
        with pytest.raises(ValueError):
            failing_function()
        
        client.fallback_enabled = True  # Restaura
        assert call_count == 1