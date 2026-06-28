import pytest
from redis_simplify import RedisClient

# ============ FIXTURE BÁSICAS ============

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

# ============ FIXTURE DE LIMPEZA ============

@pytest.fixture
def clean_client(client):
    """Limpa o banco antes e depois de cada teste"""
    client.flushall()
    yield client
    client.flushall()