import pytest
from redis_simplify import RedisClient

@pytest.fixture
def client():
    """Fixture compartilhada - cria cliente Redis para testes"""
    return RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        fallback_enabled=True  # ← Fallback habilitado para testes
    )

@pytest.fixture
def client_no_fallback():
    """Fixture com fallback desabilitado"""
    return RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        fallback_enabled=False  # ← Fallback desabilitado para testes específicos
    )

@pytest.fixture
def clean_client(client):
    """Limpa o banco antes e depois de cada teste"""
    client.flushall()
    yield client
    client.flushall()

@pytest.fixture
def client_with_metrics(client):
    """Cliente com métricas habilitadas"""
    client.enable_metrics()
    yield client
    client.disable_metrics()
    client.reset_metrics()

@pytest.fixture
def client_from_url():
    """Cliente criado via from_url"""
    return RedisClient.from_url(
        'redis://localhost:6379/9',
        log_level="INFO",
        fallback_enabled=True
    )

@pytest.fixture
def clean_client_url(client_from_url):
    """Limpa o banco antes e depois de cada teste (via URL)"""
    client_from_url.flushall()
    yield client_from_url
    client_from_url.flushall()

@pytest.fixture(autouse=True)
def close_client_after_test(request):
    """Garante que o cliente seja fechado após cada teste"""
    def fin():
        client = getattr(request, '_client', None)
        if client:
            try:
                client.close()
            except:
                pass
    request.addfinalizer(fin)