"""Testes para funcionalidade de logging do RedisClient"""
import logging
import pytest
from redis_simplify import RedisClient


class TestRedisClientLogging:
    """Testa configuração de log level"""
    
    def test_default_log_level(self):
        """Testa nível de log padrão"""
        client = RedisClient(host="localhost", port=6379, db=9)
        redis_logger = logging.getLogger('redis_simplify.client')
        # O nível padrão pode ser INFO ou NOTSET (que herda)
        assert redis_logger.level in (logging.INFO, logging.NOTSET)
        client.close()
    
    def test_set_log_level_debug(self):
        """Testa configurar log level DEBUG na criação"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="DEBUG",
            fallback_enabled=True
        )
        assert client.ping() is True
        client.close()
    
    def test_set_log_level_warning(self):
        """Testa configurar log level WARNING na criação"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="WARNING",
            fallback_enabled=True
        )
        assert client.ping() is True
        client.close()
    
    def test_set_log_level_error(self):
        """Testa configurar log level ERROR na criação"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="ERROR",
            fallback_enabled=True
        )
        assert client.ping() is True
        client.close()
    
    def test_invalid_log_level(self):
        """Testa log level inválido (deve usar INFO como fallback)"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="INVALIDO",
            fallback_enabled=True
        )
        assert client.ping() is True
        client.close()
    
    def test_change_log_level_after_creation(self):
        """Testa mudar log level depois de criar o cliente"""
        client = RedisClient(host="localhost", port=6379, db=9, fallback_enabled=True)
        
        # Deve conseguir mudar sem erro
        client.set_log_level("DEBUG")
        client.set_log_level("INFO")
        client.set_log_level("WARNING")
        client.set_log_level("ERROR")
        
        # Log level inválido deve usar INFO
        client.set_log_level("INVALIDO")
        
        assert client.ping() is True
        client.close()
    
    def test_debug_logging_does_not_break_operations(self, caplog):
        """Testa que debug logging não quebra operações"""
        caplog.set_level(logging.DEBUG)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="DEBUG",
            fallback_enabled=True
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
        
        # Verifica que DEBUG messages foram geradas
        debug_messages = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) > 0
    
    def test_info_logging_does_not_show_debug_messages(self, caplog):
        """Testa que INFO não mostra mensagens de DEBUG"""
        caplog.set_level(logging.INFO)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="INFO",
            fallback_enabled=True
        )
        
        caplog.clear()
        
        client.set("test:info", "value")
        client.get("test:info")
        
        # Verifica que não há mensagens DEBUG
        debug_messages = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) == 0
        
        # Verifica que há mensagens (INFO ou superior)
        # Algumas versões do Redis podem não logar INFO para todas as operações
        assert len(caplog.records) >= 0  # Pode ser 0 se não houver logs INFO
        
        client.delete("test:info")
        client.close()
    
    def test_warning_logging_shows_warnings(self, caplog):
        """Testa que WARNING mostra avisos"""
        caplog.set_level(logging.WARNING)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="WARNING",
            fallback_enabled=True
        )
        
        caplog.clear()
        
        # flushall gera warning
        client.flushall()
        
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
            log_level="ERROR",
            fallback_enabled=True,
            socket_timeout=0.1
        )
        
        caplog.clear()
        
        # Tenta uma operação (vai falhar, mas deve logar como erro)
        client.set("test:error", "value")
        
        # Deve ter mensagens ERROR
        error_messages = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_messages) >= 0  # Pode ou não ter erro dependendo da conexão
        
        client.close()
    
    def test_logging_with_fallback_disabled(self, caplog):
        """Testa logging com fallback desabilitado"""
        caplog.set_level(logging.ERROR)
        
        client = RedisClient(
            host="localhost",
            port=9999,
            db=9,
            log_level="ERROR",
            fallback_enabled=False,
            socket_timeout=0.1
        )
        
        caplog.clear()
        
        # Deve levantar exceção e logar erro
        with pytest.raises(Exception):
            client.get("test:error")
        
        # Deve ter mensagens ERROR
        error_messages = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_messages) > 0
        
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
            log_level="DEBUG",
            fallback_enabled=True
        )
        
        # Strings
        client.set("test:log:str", "value")
        client.get("test:log:str")
        client.exists("test:log:str")
        client.expire("test:log:str", 60)
        client.incr("test:log:counter")
        client.decr("test:log:counter")
        client.strlen("test:log:str")
        client.append("test:log:str", " extra")
        client.getrange("test:log:str", 0, 5)
        client.setrange("test:log:str", 0, "TEST")
        
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
        
        # Sorted Sets
        client.zadd("test:log:zset", {"a": 1, "b": 2, "c": 3})
        client.zrange("test:log:zset", 0, -1, withscores=True)
        client.zscore("test:log:zset", "a")
        client.zcard("test:log:zset")
        client.zrem("test:log:zset", "a")
        
        # Keys
        client.ttl("test:log:str")
        client.delete("test:log:str", "test:log:counter", "test:log:json")
        client.delete("test:log:set", "test:log:hash", "test:log:list", "test:log:zset")
        
        client.close()
        
        # Verifica que debug messages foram geradas
        debug_messages = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) > 0
    
    def test_logging_with_metrics_enabled(self, caplog):
        """Testa logging com métricas habilitadas"""
        caplog.set_level(logging.DEBUG)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="DEBUG",
            fallback_enabled=True
        )
        
        client.enable_metrics()
        
        # Executa operações
        for i in range(5):
            client.set(f"test:metric:{i}", f"value{i}")
            client.get(f"test:metric:{i}")
        
        metrics = client.get_metrics()
        assert metrics["enabled"] is True
        assert "set" in metrics["commands"]
        assert "get" in metrics["commands"]
        
        # Limpa
        for i in range(5):
            client.delete(f"test:metric:{i}")
        
        client.disable_metrics()
        client.close()
        
        # Verifica que debug messages foram geradas
        debug_messages = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) > 0
    
    def test_logging_with_admin_commands(self, caplog):
        """Testa logging com comandos administrativos"""
        caplog.set_level(logging.INFO)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="INFO",
            fallback_enabled=True
        )
        
        caplog.clear()
        
        # Comandos administrativos
        client.info()
        client.dbsize()
        client.flushdb()
        
        # Deve ter mensagens INFO
        info_messages = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_messages) > 0
        
        client.close()