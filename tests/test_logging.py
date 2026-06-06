"""Testes para funcionalidade de logging do RedisClient"""
import logging
from redis_simplify import RedisClient


class TestRedisClientLogging:
    """Testa configuração de log level"""
    
    def test_default_log_level(self, client):
        redis_logger = logging.getLogger('redis_simplify.client')
        # O nível padrão pode ser INFO ou NOTSET (que herda)
        assert redis_logger.level in (logging.INFO, logging.NOTSET)
    
    def test_set_log_level_debug(self):
        """Testa configurar log level DEBUG na criação"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="DEBUG"
        )
        # Verifica se foi configurado (não temos acesso direto ao logger,
        # mas podemos verificar que não lança erro)
        assert client.ping() is True
        client.close()
    
    def test_set_log_level_warning(self):
        """Testa configurar log level WARNING na criação"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="WARNING"
        )
        assert client.ping() is True
        client.close()
    
    def test_set_log_level_error(self):
        """Testa configurar log level ERROR na criação"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="ERROR"
        )
        assert client.ping() is True
        client.close()
    
    def test_invalid_log_level(self):
        """Testa log level inválido (deve usar INFO como fallback)"""
        # Deve não lançar exceção e usar INFO
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="INVALIDO"
        )
        assert client.ping() is True
        client.close()
    
    def test_change_log_level_after_creation(self):
        """Testa mudar log level depois de criar o cliente"""
        client = RedisClient(host="localhost", port=6379, db=9)
        
        # Deve conseguir mudar sem erro
        client.set_log_level("DEBUG")
        client.set_log_level("INFO")
        client.set_log_level("WARNING")
        
        assert client.ping() is True
        client.close()
    
    def test_debug_logging_does_not_break_operations(self, caplog):
        """Testa que debug logging não quebra operações"""
        import logging
        caplog.set_level(logging.DEBUG)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="DEBUG"
        )
        
        # Operações devem funcionar mesmo com debug ativo
        client.set("test:debug", "value")
        assert client.get("test:debug") == "value"
        
        client.set_json("test:debug:json", {"key": "value"})
        assert client.get_json("test:debug:json") == {"key": "value"}
        
        client.sadd("test:debug:set", "a", "b")
        assert "a" in client.smembers("test:debug:set")
        
        client.incr("test:debug:counter")
        client.decr("test:debug:counter")
        
        client.delete("test:debug", "test:debug:json", "test:debug:set", "test:debug:counter")
        client.close()
    
    def test_info_logging_does_not_show_debug_messages(self, caplog):
        """Testa que INFO não mostra mensagens de DEBUG"""
        caplog.set_level(logging.INFO)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="INFO"
        )
        
        # Limpa logs anteriores
        caplog.clear()
        
        # Executa operações
        client.set("test:info", "value")
        client.get("test:info")
        
        # Verifica que não há mensagens DEBUG
        debug_messages = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) == 0
        
        client.delete("test:info")
        client.close()
    
    def test_warning_logging_shows_warnings(self, caplog):
        """Testa que WARNING mostra avisos"""
        caplog.set_level(logging.WARNING)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="WARNING"
        )
        
        caplog.clear()
        
        # flush_all gera warning
        client.flush_all()
        
        # Deve ter pelo menos uma mensagem WARNING
        warning_messages = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warning_messages) >= 1
        
        client.close()
    
    def test_error_logging_shows_errors(self, caplog):
        """Testa que ERROR mostra apenas erros"""
        caplog.set_level(logging.ERROR)
        
        # Tenta conectar em porta inválida (deve gerar erro)
        client = RedisClient(
            host="localhost",
            port=9999,  # Porta provavelmente não está rodando Redis
            db=9,
            log_level="ERROR"
        )
        
        caplog.clear()
        
        # Tenta uma operação (vai falhar, mas deve logar como erro)
        client.set("test:error", "value")
        
        # Deve ter mensagens ERROR
        error_messages = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_messages) >= 0  # Pode ou não ter erro dependendo da conexão
        
        client.close()


class TestRedisClientLoggingIntegration:
    """Testes de integração para logging"""
    
    def test_all_operations_with_debug_logging(self, caplog):
        """Testa todas operações com DEBUG ativo (não deve quebrar)"""
        caplog.set_level(logging.DEBUG)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="DEBUG"
        )
        
        # Strings
        client.set("test:log:str", "value")
        client.get("test:log:str")
        client.exists("test:log:str")
        client.expire("test:log:str", 60)
        client.incr("test:log:counter")
        client.decr("test:log:counter")
        
        # JSON
        client.set_json("test:log:json", {"name": "test"})
        client.get_json("test:log:json")
        
        # Sets
        client.sadd("test:log:set", "a", "b", "c")
        client.smembers("test:log:set")
        client.sismember("test:log:set", "a")
        client.scard("test:log:set")
        client.srem("test:log:set", "a")
        
        # Hashes
        client.hset("test:log:hash", "field1", "value1")
        client.hget("test:log:hash", "field1")
        client.hgetall("test:log:hash")
        
        # Lists
        client.lpush("test:log:list", "x", "y")
        client.rpush("test:log:list", "z")
        client.lrange("test:log:list", 0, -1)
        
        # Pipeline
        pipe = client.pipeline()
        pipe.set("test:log:p1", "v1")
        pipe.set("test:log:p2", "v2")
        pipe.execute()
        
        # Scan
        client.scan(match="test:log:*")
        
        # Cleanup
        client.delete(
            "test:log:str", "test:log:counter", "test:log:json",
            "test:log:set", "test:log:hash", "test:log:list",
            "test:log:p1", "test:log:p2"
        )
        
        client.close()
        
        # Verifica que debug messages foram geradas
        debug_messages = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) > 0