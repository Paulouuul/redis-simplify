"""Teste manual para verificar logs em diferentes níveis"""

import logging
import pytest
from redis_simplify import RedisClient

@pytest.mark.skip(reason="Teste manual - execute individualmente")
def test_manual_logging():
    """Teste manual - não executado automaticamente pelo pytest"""
    
    # Configura logging para mostrar no console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    print("\n=== TESTE COM DEBUG ===\n")
    client_debug = RedisClient(host="localhost", port=6379, db=9, log_level="DEBUG")
    client_debug.set("test", "hello")
    client_debug.get("test")
    client_debug.set_json("user", {"name": "João"})
    client_debug.get_json("user")
    client_debug.delete("test", "user")
    client_debug.close()

    print("\n=== TESTE COM INFO ===\n")
    client_info = RedisClient(host="localhost", port=6379, db=9, log_level="INFO")
    client_info.set("test", "hello")
    client_info.get("test")
    client_info.close()

    print("\n=== TESTE COM WARNING ===\n")
    client_warning = RedisClient(host="localhost", port=6379, db=9, log_level="WARNING")
    client_warning.flushall()  # Deve mostrar warning
    client_warning.close()

if __name__ == "__main__":
    test_manual_logging()