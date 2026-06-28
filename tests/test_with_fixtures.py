# test_with_fixtures.py
import pytest
import time
from redis_simplify import RedisClient

@pytest.fixture
def client_via_init():
    """Cliente criado via __init__"""
    return RedisClient(
        host='localhost',
        port=6379,
        db=9,
        log_level='INFO',
        fallback_enabled=True,
        retry_attempts=3
    )

@pytest.fixture
def client_via_url():
    """Cliente criado via from_url"""
    return RedisClient.from_url(
        'redis://localhost:6379/9',
        log_level='INFO',
        fallback_enabled=True,
        retry_attempts=3
    )

@pytest.fixture
def client_no_fallback():
    """Cliente criado com fallback desabilitado"""
    return RedisClient(
        host='localhost',
        port=6379,
        db=9,
        log_level='INFO',
        fallback_enabled=False,
        retry_attempts=3
    )

@pytest.fixture
def client_with_retry():
    """Cliente criado com retry customizado"""
    return RedisClient(
        host='localhost',
        port=6379,
        db=9,
        log_level='INFO',
        fallback_enabled=True,
        retry_attempts=5
    )

def test_init_fixture(client_via_init):
    """Testa cliente criado via __init__"""
    assert client_via_init.ping() is True
    assert client_via_init.fallback_enabled is True
    assert client_via_init.retry_attempts == 3
    
    client_via_init.set('test', 'value')
    assert client_via_init.get('test') == 'value'
    
    # SET com GET
    old_value = client_via_init.set('test', 'new_value', get=True)
    assert old_value == 'value'
    
    # JSON com RedisJSON
    client_via_init.set_json('test:json', {'name': 'test', 'age': 30})
    assert client_via_init.get_json('test:json') == {'name': 'test', 'age': 30}
    
    # JSON com caminho específico
    client_via_init.set_json_path('test:json', '$.age', 31)
    age = client_via_init.get_json_path('test:json', '$.age')
    assert age == 31
    
    # Sets
    client_via_init.sadd('test:set', 'a', 'b', 'c')
    assert 'a' in client_via_init.smembers('test:set')
    
    # Sorted Sets com opções avançadas
    client_via_init.zadd('test:zset', {'a': 1, 'b': 2, 'c': 3})
    results = client_via_init.zrange('test:zset', 1, 3, byscore=True, withscores=True)
    assert len(results) >= 1
    
    # Limpeza
    client_via_init.delete('test', 'test:json', 'test:set', 'test:zset')
    client_via_init.close()

def test_url_fixture(client_via_url):
    """Testa cliente criado via from_url"""
    assert client_via_url.ping() is True
    assert client_via_url.fallback_enabled is True
    assert client_via_url.retry_attempts == 3
    assert client_via_url.host == 'localhost'
    assert client_via_url.port == 6379
    assert client_via_url.db == 9
    
    client_via_url.set('test', 'value')
    assert client_via_url.get('test') == 'value'
    
    # GETDEL
    value = client_via_url.getdel('test')
    assert value == 'value'
    assert client_via_url.exists('test') is False
    
    # JSON
    client_via_url.set_json('test:json', {'name': 'test'})
    assert client_via_url.get_json('test:json') == {'name': 'test'}
    
    # EXPIRE com NX
    client_via_url.set('test:expire', 'value')
    client_via_url.expire('test:expire', 60, nx=True)
    
    # Limpeza
    client_via_url.delete('test:json', 'test:expire')
    client_via_url.close()

def test_no_fallback_fixture(client_no_fallback):
    """Testa cliente com fallback desabilitado"""
    assert client_no_fallback.ping() is True
    assert client_no_fallback.fallback_enabled is False
    assert client_no_fallback.retry_attempts == 3
    
    client_no_fallback.set('test', 'value')
    assert client_no_fallback.get('test') == 'value'
    
    # Para testar exceção, forçamos erro de conexão
    bad_client = RedisClient(host='localhost', port=9999, fallback_enabled=False, retry_attempts=1)
    with pytest.raises(Exception):
        bad_client.get('test')
    bad_client.close()
    
    client_no_fallback.delete('test')
    client_no_fallback.close()

def test_retry_fixture(client_with_retry):
    """Testa cliente com retry customizado"""
    assert client_with_retry.retry_attempts == 5
    assert client_with_retry.ping() is True
    
    client_with_retry.set('test', 'value')
    assert client_with_retry.get('test') == 'value'
    
    # Sorted Set com ZADD GT
    client_with_retry.zadd('test:zset', {'a': 1})
    client_with_retry.zadd('test:zset', {'a': 2}, gt=True)
    score = client_with_retry.zscore('test:zset', 'a')
    assert score == 2.0
    
    client_with_retry.delete('test', 'test:zset')
    client_with_retry.close()

def test_both_in_same_test():
    """Testa ambos na mesma função"""
    client1 = RedisClient(host='localhost', port=6379, db=9, fallback_enabled=True, retry_attempts=3)
    client2 = RedisClient.from_url('redis://localhost:6379/9', fallback_enabled=True, retry_attempts=3)
    
    assert client1.ping() is True
    assert client2.ping() is True
    
    assert client1.fallback_enabled is True
    assert client2.fallback_enabled is True
    
    client1.set('key1', 'value1')
    client2.set('key2', 'value2')
    
    assert client1.get('key1') == 'value1'
    assert client2.get('key2') == 'value2'
    
    assert client1.get('chave_inexistente') is None
    assert client2.get('chave_inexistente') is None
    
    # JSON com ambos
    client1.set_json('test:json', {'id': 1})
    client2.set_json('test:json2', {'id': 2})
    
    assert client1.get_json('test:json') == {'id': 1}
    assert client2.get_json('test:json2') == {'id': 2}
    
    client1.delete('key1', 'test:json')
    client2.delete('key2', 'test:json2')
    client1.close()
    client2.close()

def test_update_url_from_fixture(client_via_init):
    """Testa reconfigurar cliente via URL"""
    assert client_via_init.host == 'localhost'
    assert client_via_init.port == 6379
    
    client_via_init.update_url('redis://localhost:6379/9')
    assert client_via_init._url == 'redis://localhost:6379/9'
    assert client_via_init.ping() is True
    
    client_via_init.set('test:after', 'value')
    assert client_via_init.get('test:after') == 'value'
    
    # SET com KEEPTTL
    client_via_init.expire('test:after', 60)
    client_via_init.set('test:after', 'new_value', keepttl=True)
    
    client_via_init.delete('test:after')
    client_via_init.close()

def test_fallback_context_with_fixtures(client_via_init):
    """Testa context manager de fallback com fixtures"""
    assert client_via_init.get('chave_inexistente') is None
    
    with client_via_init.fallback_context(False):
        value = client_via_init.get('chave_inexistente')
        assert value is None
    
    assert client_via_init.get('chave_inexistente') is None
    assert client_via_init.fallback_enabled is True
    
    client_via_init.close()

def test_metrics_with_fixtures(client_via_init):
    """Testa métricas com fixtures"""
    client_via_init.enable_metrics()
    assert client_via_init._metrics_enabled is True
    
    client_via_init.set('test:metric', 'value')
    client_via_init.get('test:metric')
    client_via_init.set_json('test:metric:json', {'key': 'value'})
    client_via_init.zadd('test:metric:zset', {'a': 1})
    
    metrics = client_via_init.get_metrics()
    assert metrics["enabled"] is True
    assert "set" in metrics["commands"]
    assert "get" in metrics["commands"]
    assert "set_json" in metrics["commands"]
    assert "zadd" in metrics["commands"]
    
    client_via_init.delete('test:metric', 'test:metric:json', 'test:metric:zset')
    client_via_init.disable_metrics()
    client_via_init.close()

def test_admin_commands_with_fixtures(client_via_init):
    """Testa comandos administrativos com fixtures"""
    info = client_via_init.info()
    assert 'redis_version' in info
    
    sections = client_via_init.info_sections()
    assert len(sections) > 0
    
    dbsize = client_via_init.dbsize()
    assert isinstance(dbsize, int)
    
    # SCAN com tipo
    client_via_init.set('test:scan:string', 'value')
    cursor, keys = client_via_init.scan(match='test:scan:*', type='string')
    assert len(keys) > 0
    
    # Memory usage
    usage = client_via_init.memory_usage('test:scan:string')
    assert usage is not None and usage > 0
    
    client_via_init.delete('test:scan:string')
    client_via_init.close()

def test_set_retry_attempts_with_fixtures(client_via_init):
    """Testa alterar retry attempts com fixtures"""
    assert client_via_init.retry_attempts == 3
    
    client_via_init.set_retry_attempts(5, backoff_base=2.0)
    assert client_via_init.retry_attempts == 5
    assert client_via_init.extra_kwargs.get('backoff_base') == 2.0
    assert client_via_init.ping() is True
    
    client_via_init.close()

def test_json_advanced_with_fixtures(client_via_init):
    """Testa operações JSON avançadas com fixtures"""
    # Criar JSON com array
    client_via_init.set_json('test:json:array', {
        'name': 'test',
        'tags': ['python', 'redis']
    })
    
    # Adicionar ao array
    client_via_init.arrappend_json('test:json:array', '$.tags', 'fastapi')
    length = client_via_init.arrlen_json('test:json:array', '$.tags')
    assert length == 3
    
    # Remover do array
    removed = client_via_init.arrpop_json('test:json:array', '$.tags')
    assert removed == 'fastapi'
    
    # Limpar
    client_via_init.clear_json('test:json:array', '$.tags')
    tags = client_via_init.get_json_path('test:json:array', '$.tags')
    assert tags == []
    
    client_via_init.delete('test:json:array')
    client_via_init.close()

def test_pubsub_with_fixtures(client_via_init):
    """Testa Pub/Sub com fixtures"""
    received = []
    
    def callback(channel, message):
        received.append((channel, message))
    
    client_via_init.subscribe('test:pubsub:channel', callback)
    time.sleep(0.1)
    
    # Publish com nohistory
    client_via_init.publish('test:pubsub:channel', 'Hello with nohistory!', nohistory=True)
    client_via_init.publish_json('test:pubsub:channel', {'type': 'test', 'data': 'json'})
    
    time.sleep(0.1)
    assert len(received) >= 1
    
    client_via_init.close_pubsubs()
    client_via_init.close()