# test_connection.py
import pytest
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
            log_level='INFO'
        )
        
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 0
        assert client.client is not None
        assert client.ping() is True
        
        client.close()
    
    def test_init_with_defaults(self):
        """Testa criação com valores padrão"""
        client = RedisClient()
        
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 0
        assert client.ping() is True
        
        client.close()
    
    def test_init_with_kwargs(self):
        """Testa criação com kwargs extras"""
        client = RedisClient(
            host='localhost',
            port=6379,
            db=9,  # ← Use DB de teste!
            socket_timeout=5,
            socket_connect_timeout=3
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
        client = RedisClient.from_url('redis://localhost:6379/0')
        
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 0
        assert client.ping() is True
        
        client.close()
    
    def test_from_url_with_password(self):
        """Testa parsing de URL com senha (sem conexão real)"""
        # Testa apenas o parsing, não a conexão
        client = RedisClient.from_url('redis://:senha123@localhost:6379/9')
        assert client.password == 'senha123'
        assert client.host == 'localhost'
        assert client.port == 6379
        assert client.db == 9

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
            'redis://localhost:6379/0',
            decode_responses=False,
            socket_timeout=10
        )
        
        assert client.decode_responses is False
        assert client.extra_kwargs.get('socket_timeout') == 10
        assert client.ping() is True
        
        client.close()
    
    def test_from_url_invalid(self):
        """Testa URL inválida - cliente deve falhar silenciosamente"""
        client = RedisClient.from_url('redis://localhost:9999/9')
        
        # Verifica que a conexão falhou
        assert client.client is None or client.ping() is False
        
        client.close()

class TestRedisClientBothMethods:
    """Testes comparando ambas as formas"""
    
    def test_both_methods_produce_same_type(self):
        """Verifica que ambas as formas produzem o mesmo tipo"""
        client1 = RedisClient(host='localhost', port=6379)
        client2 = RedisClient.from_url('redis://localhost:6379/0')
        
        assert type(client1) == type(client2)
        assert isinstance(client1, RedisClient)
        assert isinstance(client2, RedisClient)
        
        client1.close()
        client2.close()
    
    def test_both_methods_connect(self, clean_client):
        """Verifica que ambas conectam corretamente"""
        # Usando clean_client para evitar flushall em produção
        assert clean_client.ping() is True
        
        client2 = RedisClient.from_url('redis://localhost:6379/9')
        assert client2.ping() is True
        client2.close()
    
    def test_update_url_from_init(self):
        """Testa reconfigurar cliente criado com __init__"""
        client = RedisClient(host='localhost', port=6379)
        assert client.host == 'localhost'
        
        # Reconfigura com URL
        client.update_url('redis://outrohost:6379/0')
        assert client._url == 'redis://outrohost:6379/0'
        # O host pode ser atualizado após reconexão
        
        client.close()