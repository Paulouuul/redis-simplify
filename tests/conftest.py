import pytest
from redis_simplify import RedisClient

@pytest.fixture
def client():
    """Fixture compartilhada - cria cliente Redis para testes"""
    # Usa DB 9 para não conflitar com dados reais
    return RedisClient(host="localhost", port=6379, db=9)

@pytest.fixture
def clean_client(client):
    """Limpa o banco antes e depois de cada teste"""
    client.flush_all()  # Limpa antes
    yield client
    client.flush_all()  # Limpa depois