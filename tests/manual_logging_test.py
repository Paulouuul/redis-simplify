"""Teste manual para verificar logs em diferentes níveis"""

import logging
import pytest
from redis_simplify import RedisClient

def test_manual_logging():
    """Teste manual - não executado automaticamente pelo pytest"""
    
    # Configura logging para mostrar no console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    print("\n" + "="*50)
    print("TESTE COM DEBUG")
    print("="*50 + "\n")
    
    client_debug = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="DEBUG",
        fallback_enabled=True
    )
    
    # Operações básicas
    client_debug.set("test", "hello")
    client_debug.get("test")
    
    # JSON
    client_debug.set_json("user", {"name": "João"})
    client_debug.get_json("user")
    
    # Keys
    client_debug.exists("test")
    client_debug.ttl("test")
    
    # Admin
    client_debug.dbsize()
    
    # Limpeza
    client_debug.delete("test", "user")
    client_debug.close()

    print("\n" + "="*50)
    print("TESTE COM INFO")
    print("="*50 + "\n")
    
    client_info = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="INFO",
        fallback_enabled=True
    )
    
    client_info.set("test", "hello")
    client_info.get("test")
    client_info.set_json("user", {"name": "Maria"})
    client_info.get_json("user")
    client_info.delete("test", "user")
    client_info.close()

    print("\n" + "="*50)
    print("TESTE COM WARNING")
    print("="*50 + "\n")
    
    client_warning = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="WARNING",
        fallback_enabled=True
    )
    
    # Operações que geram warnings
    client_warning.flushall()  # Deve mostrar warning
    client_warning.delete("chave_inexistente")  # Pode gerar warning
    
    # Tentativa de operação em chave inexistente
    client_warning.get("chave_que_nao_existe")
    
    client_warning.close()

    print("\n" + "="*50)
    print("TESTE COM ERROR (fallback desabilitado)")
    print("="*50 + "\n")
    
    client_error = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="ERROR",
        fallback_enabled=False  # ← Sem fallback, levanta exceções
    )
    
    try:
        # Isso vai falhar e mostrar erro
        client_error.get("chave_inexistente_com_erro")
    except Exception as e:
        print(f"❌ Exceção capturada (esperado): {e}")
    
    client_error.close()

    print("\n" + "="*50)
    print("TESTE COM MÉTRICAS")
    print("="*50 + "\n")
    
    client_metrics = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="DEBUG",
        fallback_enabled=True
    )
    
    # Habilita métricas
    client_metrics.enable_metrics()
    
    # Executa operações
    for i in range(5):
        client_metrics.set(f"metric:key:{i}", f"value{i}")
        client_metrics.get(f"metric:key:{i}")
    
    # Mostra métricas
    metrics = client_metrics.get_metrics()
    print(f"Métricas coletadas: {len(metrics.get('commands', {}))} comandos")
    
    for cmd, data in metrics.get('commands', {}).items():
        print(f"  {cmd}: {data['count']} chamadas, média {data['avg_time_ms']}ms")
    
    # Limpeza
    for i in range(5):
        client_metrics.delete(f"metric:key:{i}")
    
    client_metrics.disable_metrics()
    client_metrics.close()

    print("\n" + "="*50)
    print("TESTES CONCLUÍDOS")
    print("="*50 + "\n")


def test_from_url_logging():
    """Teste de configuração via URL com logging"""
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    print("\n" + "="*50)
    print("TESTE COM FROM_URL")
    print("="*50 + "\n")
    
    # Usando URL
    client = RedisClient.from_url(
        "redis://localhost:6379/9",
        log_level="DEBUG",
        fallback_enabled=True
    )
    
    client.set("url:test", "value")
    client.get("url:test")
    client.delete("url:test")
    client.close()


if __name__ == "__main__":
    test_manual_logging()
    test_from_url_logging()