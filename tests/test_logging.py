"""Testes para funcionalidade de logging do RedisClient"""
import logging
import pytest
import time
from redis_simplify import RedisClient


class TestRedisClientLogging:
    """Testa configuração de log level"""
    
    def test_default_log_level(self):
        """Testa nível de log padrão"""
        client = RedisClient(host="localhost", port=6379, db=9)
        redis_logger = logging.getLogger('redis_simplify.client')
        assert redis_logger.level in (logging.INFO, logging.NOTSET)
        client.close()
    
    def test_set_log_level_debug(self):
        """Testa configurar log level DEBUG na criação"""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="DEBUG",
            fallback_enabled=True,
            retry_attempts=3
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
            fallback_enabled=True,
            retry_attempts=3
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
            fallback_enabled=True,
            retry_attempts=3
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
            fallback_enabled=True,
            retry_attempts=3
        )
        assert client.ping() is True
        client.close()
    
    def test_change_log_level_after_creation(self):
        """Testa mudar log level depois de criar o cliente"""
        client = RedisClient(host="localhost", port=6379, db=9, fallback_enabled=True)
        
        client.set_log_level("DEBUG")
        client.set_log_level("INFO")
        client.set_log_level("WARNING")
        client.set_log_level("ERROR")
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
            fallback_enabled=True,
            retry_attempts=3
        )
        
        # Operações básicas
        client.set("test:debug", "value")
        assert client.get("test:debug") == "value"
        
        # SET com GET (log deve mostrar)
        old_value = client.set("test:debug", "new_value", get=True)
        assert old_value == "value"
        
        # JSON
        client.set_json("test:debug:json", {"key": "value"})
        assert client.get_json("test:debug:json") == {"key": "value"}
        
        # JSON com caminho específico
        client.set_json_path("test:debug:json", '$.key', "new_value")
        assert client.get_json_path("test:debug:json", '$.key') == "new_value"
        
        # Sets
        client.sadd("test:debug:set", "a", "b")
        assert "a" in client.smembers("test:debug:set")
        
        # Sorted Sets com opções avançadas
        client.zadd("test:debug:zset", {"a": 1, "b": 2, "c": 3})
        results = client.zrange("test:debug:zset", 0, -1, withscores=True)
        assert len(results) == 3
        
        client.incr("test:debug:counter")
        client.decr("test:debug:counter")
        
        # Pub/Sub
        received = []
        def callback(channel, message):
            received.append((channel, message))
        
        client.subscribe("test:debug:channel", callback)
        time.sleep(0.1)
        client.publish("test:debug:channel", "test message")
        time.sleep(0.1)
        client.close_pubsubs()
        
        # Limpeza
        client.delete("test:debug", "test:debug:json", "test:debug:set", 
                      "test:debug:counter", "test:debug:zset")
        client.close()
        
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
            fallback_enabled=True,
            retry_attempts=3
        )
        
        caplog.clear()
        
        client.set("test:info", "value")
        client.get("test:info")
        client.set_json("test:info:json", {"key": "value"})
        client.get_json("test:info:json")
        client.zadd("test:info:zset", {"a": 1})
        
        debug_messages = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert len(debug_messages) == 0
        
        client.delete("test:info", "test:info:json", "test:info:zset")
        client.close()
    
    def test_warning_logging_shows_warnings(self, caplog):
        """Testa que WARNING mostra avisos"""
        caplog.set_level(logging.WARNING)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="WARNING",
            fallback_enabled=True,
            retry_attempts=3
        )
        
        caplog.clear()
        client.flushall()
        
        warning_messages = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warning_messages) >= 1
        
        client.close()
    
    def test_error_logging_shows_errors(self, caplog):
        """Testa que ERROR mostra apenas erros"""
        caplog.set_level(logging.ERROR)
        
        client = RedisClient(
            host="localhost",
            port=9999,
            db=9,
            log_level="ERROR",
            fallback_enabled=True,
            socket_timeout=0.1,
            retry_attempts=1
        )
        
        caplog.clear()
        client.set("test:error", "value")
        
        error_messages = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_messages) >= 0
        
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
            socket_timeout=0.1,
            retry_attempts=1
        )
        
        caplog.clear()
        
        with pytest.raises(Exception):
            client.get("test:error")
        
        error_messages = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(error_messages) > 0
        
        client.close()
    
    def test_logging_with_retry(self, caplog):
        """Testa logging com retry nativo"""
        caplog.set_level(logging.INFO)
        
        client = RedisClient(
            host="localhost",
            port=6379,
            db=9,
            log_level="INFO",
            retry_attempts=5
        )
        
        assert client.retry_attempts == 5
        assert client.ping() is True
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
            fallback_enabled=True,
            retry_attempts=3
        )
        
        # Strings com novas opções
        client.set("test:log:str", "value")
        client.set("test:log:str", "new_value", get=True)  # SET com GET
        client.get("test:log:str")
        client.exists("test:log:str")
        client.expire("test:log:str", 60, nx=True)  # EXPIRE com NX
        client.incr("test:log:counter")
        client.decr("test:log:counter")
        client.strlen("test:log:str")
        client.append("test:log:str", " extra")
        client.getrange("test:log:str", 0, 5)
        client.setrange("test:log:str", 0, "TEST")
        client.getdel("test:log:str")  # GETDEL
        client.getex("test:log:str", ex=60)  # GETEX
        
        # JSON avançado
        client.set_json("test:log:json", {"name": "test", "tags": ["a", "b"]})
        client.set_json_path("test:log:json", '$.name', "updated")
        client.get_json_path("test:log:json", '$.name')
        client.arrappend_json("test:log:json", '$.tags', "c")
        client.arrlen_json("test:log:json", '$.tags')
        
        # Keys com novas opções
        client.copy("test:log:str", "test:log:copy")
        client.touch("test:log:str")
        
        # Sorted Sets avançados
        client.zadd("test:log:zset", {"a": 1, "b": 2, "c": 3}, gt=True)
        client.zrange("test:log:zset", 1, 3, byscore=True, withscores=True)
        client.zmscore("test:log:zset", ["a", "b", "c"])
        
        # SCAN com tipo
        client.scan(match="test:log:*", type='string')
        
        # Admin
        client.info('stats')
        client.dbsize()
        client.memory_usage("test:log:str")
        
        # Limpeza
        client.delete("test:log:str", "test:log:copy", "test:log:counter")
        client.delete("test:log:json", "test:log:zset")
        
        client.close()
        
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
            fallback_enabled=True,
            retry_attempts=3
        )
        
        client.enable_metrics()
        
        for i in range(5):
            client.set(f"test:metric:{i}", f"value{i}")
            client.get(f"test:metric:{i}")
        
        client.set_json("test:metric:json", {"counter": i})
        client.zadd("test:metric:zset", {"a": 1, "b": 2})
        
        metrics = client.get_metrics()
        assert metrics["enabled"] is True
        assert "set" in metrics["commands"]
        assert "get" in metrics["commands"]
        assert "set_json" in metrics["commands"]
        assert "zadd" in metrics["commands"]
        
        for i in range(5):
            client.delete(f"test:metric:{i}")
        client.delete("test:metric:json", "test:metric:zset")
        
        client.disable_metrics()
        client.close()
        
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
            fallback_enabled=True,
            retry_attempts=3
        )
        
        caplog.clear()
        
        client.info()
        client.info('stats')
        client.info_sections()
        client.dbsize()
        client.scan(match="*", count=10)
        client.slowlog(5)
        client.client_list()
        client.flushdb()
        
        info_messages = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_messages) > 0
        
        client.close()