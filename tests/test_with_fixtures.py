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
        log_level='INFO'
    )

@pytest.fixture
def client_via_url():
    """Cliente criado via from_url"""
    return RedisClient.from_url(
        'redis://localhost:6379/9',
        log_level='INFO'
    )

def test_init_fixture(client_via_init):
    """Testa cliente criado via __init__"""
    assert client_via_init.ping() is True
    client_via_init.set('test', 'value')
    assert client_via_init.get('test') == 'value'
    client_via_init.close()

def test_url_fixture(client_via_url):
    """Testa cliente criado via from_url"""
    assert client_via_url.ping() is True
    client_via_url.set('test', 'value')
    assert client_via_url.get('test') == 'value'
    client_via_url.close()

def test_both_in_same_test():
    """Testa ambos na mesma função"""
    client1 = RedisClient(host='localhost', port=6379, db=9)
    client2 = RedisClient.from_url('redis://localhost:6379/9')
    
    # Verifica que ambos funcionam
    assert client1.ping() is True
    assert client2.ping() is True
    
    # Verifica que são independentes
    client1.set('key1', 'value1')
    client2.set('key2', 'value2')
    
    assert client1.get('key1') == 'value1'
    assert client2.get('key2') == 'value2'
    
    client1.close()
    client2.close()