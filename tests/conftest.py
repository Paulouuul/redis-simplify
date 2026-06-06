import pytest
from redis_simplify import RedisClient

@pytest.fixture
def client():
    """Fixture compartilhada - cria cliente Redis para testes"""
    return RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO"  # ← log level padrão para testes
    )

@pytest.fixture
def clean_client(client):
    """Limpa o banco antes e depois de cada teste"""
    client.flush_all()
    yield client
    client.flush_all()