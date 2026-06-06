"""Testes para o RedisClient"""
from redis_simplify import RedisClient


class TestRedisClientBasico:
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