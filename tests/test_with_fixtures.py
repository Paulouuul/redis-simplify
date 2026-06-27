# test_with_fixtures.py
import pytest
from redis_simplify import RedisClient

@pytest.fixture
def client_via_init():
    """Cliente criado via __init__"""
    return RedisClient(
        host='localhost',
        port=6379,
        db=9,
        log_level='INFO',
        fallback_enabled=True
    )

@pytest.fixture
def client_via_url():
    """Cliente criado via from_url"""
    return RedisClient.from_url(
        'redis://localhost:6379/9',
        log_level='INFO',
        fallback_enabled=True
    )

@pytest.fixture
def client_no_fallback():
    """Cliente criado com fallback desabilitado"""
    return RedisClient(
        host='localhost',
        port=6379,
        db=9,
        log_level='INFO',
        fallback_enabled=False
    )

def test_init_fixture(client_via_init):
    """Testa cliente criado via __init__"""
    assert client_via_init.ping() is True
    assert client_via_init.fallback_enabled is True
    
    client_via_init.set('test', 'value')
    assert client_via_init.get('test') == 'value'
    
    # Testa operações adicionais
    client_via_init.set_json('test:json', {'name': 'test'})
    assert client_via_init.get_json('test:json') == {'name': 'test'}
    
    client_via_init.sadd('test:set', 'a', 'b', 'c')
    assert 'a' in client_via_init.smembers('test:set')
    
    # Limpeza
    client_via_init.delete('test', 'test:json', 'test:set')
    client_via_init.close()

def test_url_fixture(client_via_url):
    """Testa cliente criado via from_url"""
    assert client_via_url.ping() is True
    assert client_via_url.fallback_enabled is True
    assert client_via_url.host == 'localhost'
    assert client_via_url.port == 6379
    assert client_via_url.db == 9
    
    client_via_url.set('test', 'value')
    assert client_via_url.get('test') == 'value'
    
    # Testa operações adicionais
    client_via_url.set_json('test:json', {'name': 'test'})
    assert client_via_url.get_json('test:json') == {'name': 'test'}
    
    # Limpeza
    client_via_url.delete('test', 'test:json')
    client_via_url.close()

def test_no_fallback_fixture(client_no_fallback):
    """Testa cliente com fallback desabilitado"""
    assert client_no_fallback.ping() is True
    assert client_no_fallback.fallback_enabled is False
    
    client_no_fallback.set('test', 'value')
    assert client_no_fallback.get('test') == 'value'
    
    # Para testar exceção, precisamos forçar um erro de conexão
    # Ou usar uma operação que realmente falhe
    bad_client = RedisClient(host='localhost', port=9999, fallback_enabled=False)
    with pytest.raises(Exception):
        bad_client.get('test')
    bad_client.close()
    
    client_no_fallback.delete('test')
    client_no_fallback.close()

def test_both_in_same_test():
    """Testa ambos na mesma função"""
    client1 = RedisClient(host='localhost', port=6379, db=9, fallback_enabled=True)
    client2 = RedisClient.from_url('redis://localhost:6379/9', fallback_enabled=True)
    
    # Verifica que ambos funcionam
    assert client1.ping() is True
    assert client2.ping() is True
    
    # Verifica que ambos têm fallback habilitado
    assert client1.fallback_enabled is True
    assert client2.fallback_enabled is True
    
    # Verifica que são independentes
    client1.set('key1', 'value1')
    client2.set('key2', 'value2')
    
    assert client1.get('key1') == 'value1'
    assert client2.get('key2') == 'value2'
    
    # Testa fallback
    assert client1.get('chave_inexistente') is None
    assert client2.get('chave_inexistente') is None
    
    client1.close()
    client2.close()

def test_update_url_from_fixture(client_via_init):
    """Testa reconfigurar cliente via URL"""
    assert client_via_init.host == 'localhost'
    assert client_via_init.port == 6379
    
    # Reconfigura com URL
    client_via_init.update_url('redis://localhost:6379/9')
    assert client_via_init._url == 'redis://localhost:6379/9'
    assert client_via_init.ping() is True
    
    # Testa operações após reconexão
    client_via_init.set('test:after', 'value')
    assert client_via_init.get('test:after') == 'value'
    
    client_via_init.delete('test:after')
    client_via_init.close()

def test_fallback_context_with_fixtures(client_via_init):
    """Testa context manager de fallback com fixtures"""
    # Fallback habilitado (padrão)
    assert client_via_init.get('chave_inexistente') is None
    
    # Desabilita fallback temporariamente
    with client_via_init.fallback_context(False):
        # Redis retorna None para chave inexistente (não levanta exceção)
        # Isso é comportamento esperado do Redis
        value = client_via_init.get('chave_inexistente')
        assert value is None
    
    # Volta ao normal
    assert client_via_init.get('chave_inexistente') is None
    
    # Testa que o fallback foi restaurado
    assert client_via_init.fallback_enabled is True
    
    client_via_init.close()

def test_metrics_with_fixtures(client_via_init):
    """Testa métricas com fixtures"""
    client_via_init.enable_metrics()
    assert client_via_init._metrics_enabled is True
    
    # Executa operações
    client_via_init.set('test:metric', 'value')
    client_via_init.get('test:metric')
    
    # Verifica métricas
    metrics = client_via_init.get_metrics()
    assert metrics["enabled"] is True
    assert "set" in metrics["commands"]
    assert "get" in metrics["commands"]
    
    client_via_init.delete('test:metric')
    client_via_init.disable_metrics()
    client_via_init.close()

def test_admin_commands_with_fixtures(client_via_init):
    """Testa comandos administrativos com fixtures"""
    # Comandos básicos
    info = client_via_init.info()
    assert 'redis_version' in info
    
    sections = client_via_init.info_sections()
    assert len(sections) > 0
    
    dbsize = client_via_init.dbsize()
    assert isinstance(dbsize, int)
    
    client_via_init.close()