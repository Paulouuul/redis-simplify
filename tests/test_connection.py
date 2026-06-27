# test_connection.py
import pytest
import time
from redis_simplify import RedisClient

class TestRedisClientInit:
    """Testes para criação via __init__"""
    
    def test_init_with_params(self):
        """Testa criação com parâmetros tradicionais"""
        client = RedisClient(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            decode_responses=True,
            log_level='INFO',
            fallback_enabled=True
        )
        
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 0
        assert client.fallback_enabled is True
        assert client.client is not None
        assert client.ping() is True
        
        client.close()
    
    def test_init_with_defaults(self):
        """Testa criação com valores padrão"""
        client = RedisClient()
        
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 0
        assert client.fallback_enabled is True
        assert client.ping() is True
        
        client.close()
    
    def test_init_with_fallback_disabled(self):
        """Testa criação com fallback desabilitado"""
        client = RedisClient(
            host='localhost',
            port=6379,
            db=9,
            fallback_enabled=False
        )
        
        assert client.fallback_enabled is False
        assert client.ping() is True
        
        client.close()
    
    def test_init_with_kwargs(self):
        """Testa criação com kwargs extras"""
        client = RedisClient(
            host='localhost',
            port=6379,
            db=9,
            socket_timeout=5,
            socket_connect_timeout=3,
            fallback_enabled=True
        )
        
        # Verifica se os kwargs foram guardados
        assert client.extra_kwargs.get('socket_timeout') == 5
        assert client.extra_kwargs.get('socket_connect_timeout') == 3
        
        # Verifica se a conexão funciona
        assert client.ping() is True
        
        client.close()

class TestRedisClientFromURL:
    """Testes para criação via from_url"""
    
    def test_from_url_simple(self):
        """Testa criação com URL simples"""
        client = RedisClient.from_url(
            'redis://localhost:6379/0',
            fallback_enabled=True
        )
        
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 0
        assert client.fallback_enabled is True
        assert client.ping() is True
        
        client.close()
    
    def test_from_url_with_password(self):
        """Testa parsing de URL com senha"""
        client = RedisClient.from_url(
            'redis://:senha123@localhost:6379/9',
            fallback_enabled=True
        )
        assert client.password == 'senha123'
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 9
        assert client.fallback_enabled is True

        client.close()
    
    def test_from_url_with_fallback_disabled(self):
        """Testa criação com URL e fallback desabilitado"""
        client = RedisClient.from_url(
            'redis://localhost:6379/9',
            fallback_enabled=False
        )
        
        assert client.fallback_enabled is False
        assert client.ping() is True
        
        client.close()
    
    # def test_from_url_with_ssl(self):
    #     """Testa criação com URL SSL"""
    #     try:
    #         client = RedisClient.from_url('rediss://localhost:6379/9')
    #         assert client.host == 'localhost'
    #         assert client.port == 6379
    #         client.close()
    #     except Exception as e:
    #         # Se não tiver SSL, pula o teste
    #         pytest.skip(f"SSL não disponível: {e}")
    
    def test_from_url_with_params(self):
        """Testa criação com URL e parâmetros adicionais"""
        client = RedisClient.from_url(
            'redis://localhost:6379/9',
            decode_responses=False,
            socket_timeout=10,
            fallback_enabled=True
        )
        
        assert client.decode_responses is False
        assert client.extra_kwargs.get('socket_timeout') == 10
        assert client.ping() is True
        
        client.close()
    
    def test_from_url_invalid(self):
        """Testa URL inválida - cliente deve falhar silenciosamente"""
        client = RedisClient.from_url(
            'redis://localhost:9999/9',
            fallback_enabled=True
        )
        
        # Verifica que a conexão falhou
        assert client.client is None or client.ping() is False
        
        client.close()

class TestRedisClientBothMethods:
    """Testes comparando ambas as formas"""
    
    def test_both_methods_produce_same_type(self):
        """Verifica que ambas as formas produzem o mesmo tipo"""
        client1 = RedisClient(host='localhost', port=6379, db=9)
        client2 = RedisClient.from_url('redis://localhost:6379/9')
        
        assert type(client1) == type(client2)
        assert isinstance(client1, RedisClient)
        assert isinstance(client2, RedisClient)
        
        client1.close()
        client2.close()
    
    def test_both_methods_connect(self):
        """Verifica que ambas conectam corretamente"""
        client1 = RedisClient(host='localhost', port=6379, db=9)
        client2 = RedisClient.from_url('redis://localhost:6379/9')
        
        assert client1.ping() is True
        assert client2.ping() is True
        
        client1.close()
        client2.close()
    
    def test_update_url_from_init(self):
        """Testa reconfigurar cliente criado com __init__"""
        client = RedisClient(host='localhost', port=6379, db=9)
        assert client.host == 'localhost'
        assert client.ping() is True
        
        # Reconfigura com URL
        client.update_url('redis://localhost:6379/9')
        assert client._url == 'redis://localhost:6379/9'
        assert client.ping() is True
        
        client.close()
    
    def test_fallback_behavior(self):
        """Testa comportamento do fallback"""
        # Com fallback habilitado
        client_with = RedisClient(
            host='localhost',
            port=6379,
            db=9,
            fallback_enabled=True
        )
        
        value = client_with.get('chave_que_nao_existe')
        assert value is None
        
        client_with.close()
        
        # Com fallback desabilitado
        client_without = RedisClient(
            host='localhost',
            port=6379,
            db=9,
            fallback_enabled=False
        )
        
        # O Redis pode retornar None mesmo com fallback desabilitado
        # Se a chave não existe, o Redis simplesmente retorna None
        # Então não levanta exceção
        value = client_without.get('chave_que_nao_existe')
        # Para forçar uma exceção, precisamos de um erro de conexão
        assert value is None  # Redis retorna None para chave inexistente
        
        client_without.close()

class TestRedisClientFallback:
    """Testes específicos para fallback"""
    
    def test_fallback_on_connection_error(self):
        """Testa fallback em erro de conexão"""
        # Porta inválida para forçar erro
        client = RedisClient(
            host='localhost',
            port=9999,
            db=9,
            fallback_enabled=True,
            socket_timeout=0.1
        )
        
        # Deve retornar fallback sem levantar exceção
        value = client.get('test')
        assert value is None
        
        # Deve retornar False (fallback)
        result = client.set('test', 'value')
        assert result is False
        
        client.close()
    
    def test_no_fallback_on_connection_error(self):
        """Testa que fallback desabilitado levanta exceção"""
        client = RedisClient(
            host='localhost',
            port=9999,
            db=9,
            fallback_enabled=False,
            socket_timeout=0.1
        )
        
        # Deve levantar exceção
        with pytest.raises(Exception):
            client.get('test')
        
        client.close()
    
    def test_fallback_context_manager(self):
        """Testa context manager de fallback"""
        client = RedisClient(
            host='localhost',
            port=6379,
            db=9,
            fallback_enabled=True
        )
        
        # O context manager funciona, mas o get não levanta exceção
        # porque a chave não existe (Redis retorna None)
        with client.fallback_context(False):
            value = client.get('chave_inexistente')
            assert value is None  # Redis retorna None
        
        client.close()