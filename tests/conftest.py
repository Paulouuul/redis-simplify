import pytest
from redis_simplify import RedisClient

# ============ FIXTURES BÁSICAS ============

@pytest.fixture
def client():
    """Fixture compartilhada - cria cliente Redis para testes"""
    return RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        fallback_enabled=True,
        retry_attempts=3  # ← Retry nativo
    )

@pytest.fixture
def client_no_fallback():
    """Fixture com fallback desabilitado"""
    return RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        fallback_enabled=False,
        retry_attempts=3
    )

@pytest.fixture
def client_no_retry():
    """Fixture sem retry (para testes de erro)"""
    return RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        fallback_enabled=True,
        retry_attempts=1  # ← Apenas 1 tentativa
    )

@pytest.fixture
def client_high_retry():
    """Fixture com alto número de retries"""
    return RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        fallback_enabled=True,
        retry_attempts=5  # ← 5 tentativas
    )

# ============ FIXTURES DE LIMPEZA ============

@pytest.fixture
def clean_client(client):
    """Limpa o banco antes e depois de cada teste"""
    client.flushall()
    yield client
    client.flushall()

@pytest.fixture
def clean_client_no_fallback(client_no_fallback):
    """Limpa o banco antes e depois de cada teste (sem fallback)"""
    client_no_fallback.flushall()
    yield client_no_fallback
    client_no_fallback.flushall()

# ============ FIXTURES DE MÉTRICAS ============

@pytest.fixture
def client_with_metrics(client):
    """Cliente com métricas habilitadas"""
    client.enable_metrics()
    yield client
    client.disable_metrics()
    client.reset_metrics()

@pytest.fixture
def clean_client_with_metrics(clean_client):
    """Cliente com métricas e banco limpo"""
    clean_client.enable_metrics()
    yield clean_client
    clean_client.disable_metrics()
    clean_client.reset_metrics()

# ============ FIXTURES DE URL ============

@pytest.fixture
def client_from_url():
    """Cliente criado via from_url"""
    return RedisClient.from_url(
        'redis://localhost:6379/9',
        log_level="INFO",
        fallback_enabled=True,
        retry_attempts=3
    )

@pytest.fixture
def client_from_url_no_fallback():
    """Cliente criado via from_url com fallback desabilitado"""
    return RedisClient.from_url(
        'redis://localhost:6379/9',
        log_level="INFO",
        fallback_enabled=False,
        retry_attempts=3
    )

@pytest.fixture
def clean_client_url(client_from_url):
    """Limpa o banco antes e depois de cada teste (via URL)"""
    client_from_url.flushall()
    yield client_from_url
    client_from_url.flushall()

# ============ FIXTURES DE DECORATORS ============

@pytest.fixture
def client_with_cache():
    """Cliente para testes de cache"""
    client = RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        fallback_enabled=True
    )
    client.flushall()
    yield client
    client.flushall()
    client.close()

# ============ FIXTURE DE FECHAMENTO AUTOMÁTICO ============

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

# ============ FIXTURES PARA TESTES DE JSON ============

@pytest.fixture
def json_data():
    """Dados JSON para testes"""
    return {
        "name": "João",
        "age": 30,
        "email": "joao@email.com",
        "tags": ["python", "redis"],
        "address": {
            "city": "São Paulo",
            "state": "SP"
        }
    }

@pytest.fixture
def json_data_updated():
    """Dados JSON atualizados para testes"""
    return {
        "name": "João",
        "age": 31,
        "email": "joao@email.com",
        "tags": ["python", "redis", "fastapi"],
        "address": {
            "city": "São Paulo",
            "state": "SP"
        }
    }

# ============ FIXTURES PARA TESTES DE SORTED SET ============

@pytest.fixture
def zset_data():
    """Dados para testes de sorted set"""
    return {
        "joao": 100,
        "maria": 200,
        "jose": 150,
        "ana": 50,
        "pedro": 175
    }

# ============ FIXTURES PARA TESTES DE PUB/SUB ============

@pytest.fixture
def pubsub_channel():
    """Canal para testes de Pub/Sub"""
    return "test:pubsub:channel"

@pytest.fixture
def pubsub_message():
    """Mensagem para testes de Pub/Sub"""
    return {"type": "test", "data": "hello world"}

# ============ FIXTURES PARA TESTES DE RATE LIMIT ============

@pytest.fixture
def rate_limit_key():
    """Chave para testes de rate limit"""
    return "test:ratelimit:key"

# ============ FIXTURES PARA TESTES DE LOCK ============

@pytest.fixture
def lock_name():
    """Nome para testes de lock"""
    return "test:lock:name"