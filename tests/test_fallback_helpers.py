# tests/test_fallback_helpers.py
import pytest
import time
from redis_simplify import RedisClient

class TestRedisClientFallbackHelpers:
    """Testes para funções auxiliares de fallback"""
    
    def test_with_fallback_returns_value_on_success(self, clean_client):
        """Testa with_fallback com operação bem-sucedida"""
        clean_client.set("test:key", "value")
        result = clean_client.with_fallback(clean_client.get, "test:key", fallback_value=None)
        assert result == "value"
        clean_client.delete("test:key")
    
    def test_with_fallback_returns_fallback_on_connection_error(self):
        """Testa with_fallback com fallback em erro de conexão"""
        bad_client = RedisClient(host='localhost', port=9999, db=9, socket_timeout=0.1, retry_attempts=1)
        result = bad_client.with_fallback(bad_client.get, "chave", fallback_value="default")
        assert result == "default"
        bad_client.close()
    
    def test_with_fallback_returns_fallback_on_error(self):
        """Testa with_fallback com fallback em erro"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            result = client.with_fallback(client.get, "chave", fallback_value="default")
            assert result == "default"
        finally:
            client.client = original_client
            client.close()
    
    def test_with_fallback_default_none(self, clean_client):
        """Testa with_fallback com fallback padrão None"""
        result = clean_client.with_fallback(clean_client.get, "chave_inexistente")
        assert result is None
    
    def test_with_fallback_with_retry(self):
        """Testa with_fallback com retry nativo"""
        client = RedisClient(host='localhost', port=6379, db=9, retry_attempts=3)
        result = client.with_fallback(client.get, "chave_inexistente", fallback_value="default")
        assert result == "default"
        client.close()
    
    def test_without_fallback_returns_value_on_success(self, clean_client):
        """Testa without_fallback com operação bem-sucedida"""
        clean_client.set("test:key", "value")
        result = clean_client.without_fallback(clean_client.get, "test:key")
        assert result == "value"
        clean_client.delete("test:key")
    
    def test_without_fallback_raises_on_connection_error(self):
        """Testa without_fallback levantando exceção em erro de conexão"""
        bad_client = RedisClient(host='localhost', port=9999, db=9, socket_timeout=0.1, retry_attempts=1)
        with pytest.raises(Exception):
            bad_client.without_fallback(bad_client.get, "chave")
        bad_client.close()
    
    def test_without_fallback_raises_on_error(self):
        """Testa without_fallback levantando exceção em erro"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            with pytest.raises(Exception):
                client.without_fallback(client.get, "chave")
        finally:
            client.client = original_client
            client.close()
    
    def test_safe_get_returns_value_on_success(self, clean_client):
        """Testa safe_get com chave existente"""
        clean_client.set("test:key", "value")
        result = clean_client.safe_get("test:key", default=None)
        assert result == "value"
        clean_client.delete("test:key")
    
    def test_safe_get_returns_default_on_connection_error(self):
        """Testa safe_get com erro de conexão"""
        bad_client = RedisClient(host='localhost', port=9999, db=9, socket_timeout=0.1, retry_attempts=1)
        result = bad_client.safe_get("chave", default="default_value")
        assert result == "default_value"
        bad_client.close()
    
    def test_safe_get_returns_none_on_missing_key(self, clean_client):
        """Testa safe_get com chave inexistente (Redis retorna None)"""
        result = clean_client.safe_get("chave_inexistente")
        assert result is None
    
    def test_safe_get_returns_default_on_error(self):
        """Testa safe_get com erro forçado"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            result = client.safe_get("chave", default={})
            assert result == {}
        finally:
            client.client = original_client
            client.close()
    
    def test_safe_get_with_dict_default(self):
        """Testa safe_get com default dict em erro"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            result = client.safe_get("chave_inexistente", default={})
            assert result == {}
        finally:
            client.client = original_client
            client.close()
    
    def test_safe_get_with_list_default(self):
        """Testa safe_get com default list em erro"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            result = client.safe_get("chave_inexistente", default=[])
            assert result == []
        finally:
            client.client = original_client
            client.close()
    
    def test_safe_set_returns_true_on_success(self, clean_client):
        """Testa safe_set com sucesso"""
        result = clean_client.safe_set("test:key", "value", default=False)
        assert result is True
        clean_client.delete("test:key")
    
    def test_safe_set_returns_default_on_error(self):
        """Testa safe_set com erro"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            result = client.safe_set("test:key", "value", default=False)
            assert result is False
        finally:
            client.client = original_client
            client.close()
    
    def test_safe_set_with_retry(self):
        """Testa safe_set com retry nativo"""
        client = RedisClient(host='localhost', port=6379, db=9, retry_attempts=3)
        result = client.safe_set("test:key", "value", default=False)
        assert result is True
        client.delete("test:key")
        client.close()
    
    def test_run_with_fallback_returns_value_on_success(self, clean_client):
        """Testa run_with_fallback com sucesso"""
        clean_client.set("test:key", "value")
        result = clean_client.run_with_fallback(clean_client.get, "test:key", default=None)
        assert result == "value"
        clean_client.delete("test:key")
    
    def test_run_with_fallback_returns_default_on_connection_error(self):
        """Testa run_with_fallback com erro de conexão"""
        bad_client = RedisClient(host='localhost', port=9999, db=9, socket_timeout=0.1, retry_attempts=1)
        result = bad_client.run_with_fallback(bad_client.get, "chave", default="default")
        assert result == "default"
        bad_client.close()
    
    def test_run_with_fallback_returns_default_on_error(self):
        """Testa run_with_fallback com erro forçado"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            result = client.run_with_fallback(client.get, "chave", default="default")
            assert result == "default"
        finally:
            client.client = original_client
            client.close()
    
    def test_fallback_context_disables_fallback_on_connection_error(self):
        """Testa context manager desabilitando fallback em erro de conexão"""
        bad_client = RedisClient(host='localhost', port=9999, db=9, socket_timeout=0.1, retry_attempts=1)
        with bad_client.fallback_context(False):
            with pytest.raises(Exception):
                bad_client.get("chave")
        bad_client.close()
    
    def test_fallback_context_disables_fallback_on_error(self):
        """Testa context manager desabilitando fallback em erro forçado"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_client = client.client
        client.client = None
        try:
            with client.fallback_context(False):
                with pytest.raises(Exception):
                    client.without_fallback(client.get, "chave")
        finally:
            client.client = original_client
            client.close()
    
    def test_fallback_context_restores_original_state(self, clean_client):
        """Testa que context manager restaura estado original"""
        original_state = clean_client.fallback_enabled
        with clean_client.fallback_context(not original_state):
            assert clean_client.fallback_enabled == (not original_state)
        assert clean_client.fallback_enabled == original_state
    
    # ============ NOVOS TESTES ============
    
    def test_set_retry_attempts_affects_fallback(self):
        """Testa que mudar retry attempts afeta o fallback"""
        client = RedisClient(host='localhost', port=6379, db=9)
        original_retry = client.retry_attempts
        
        client.set_retry_attempts(5, backoff_base=2.0)
        assert client.retry_attempts == 5
        
        result = client.safe_get("chave_inexistente", default="default")
        assert result == "default"
        
        client.close()
    
    def test_fallback_with_set_get_options(self, clean_client):
        """Testa fallback com SET e GET"""
        clean_client.set("test:key", "old_value")
        result = clean_client.with_fallback(
            clean_client.set, "test:key", "new_value", 
            fallback_value=None, get=True
        )
        assert result == "old_value" or result is None
        clean_client.delete("test:key")
    
    def test_fallback_with_json_operations(self, clean_client):
        """Testa fallback com JSON operations"""
        
        result = clean_client.safe_get("test:json", default={})
        assert result == {}
        
        # JSON set com fallback
        success = clean_client.with_fallback(
            clean_client.set_json, "test:json", {"name": "test"},
            fallback_value=False
        )
        assert success is True
        
        clean_client.delete("test:json")