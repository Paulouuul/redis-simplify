"""Teste manual para verificar logs em diferentes níveis"""

import logging
import pytest
import time
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
        fallback_enabled=True,
        retry_attempts=3
    )
    
    # Operações básicas
    client_debug.set("test", "hello")
    client_debug.get("test")
    
    # SET com GET (retorna valor antigo)
    old_value = client_debug.set("test", "world", get=True)
    print(f"Valor antigo do SET com GET: {old_value}")
    
    # JSON com RedisJSON nativo
    client_debug.set_json("user", {"name": "João", "age": 30})
    user = client_debug.get_json("user")
    print(f"Usuário: {user}")
    
    # JSON com caminho específico (NOVOS MÉTODOS)
    client_debug.set_json_path("user", '$.age', 31)
    age = client_debug.get_json_path("user", '$.age')
    print(f"Idade atualizada: {age}")
    
    # Keys com novas opções
    client_debug.exists("test")
    client_debug.ttl("test")
    
    # EXPIRE com condições
    client_debug.expire("test", 60, nx=True)
    
    # Admin
    client_debug.dbsize()
    
    # SCAN com tipo
    cursor, keys = client_debug.scan(match="user:*", type='hash')
    print(f"Chaves encontradas: {keys}")
    
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
        fallback_enabled=True,
        retry_attempts=3
    )
    
    client_info.set("test", "hello")
    client_info.get("test")
    client_info.set_json("user", {"name": "Maria", "tags": ["python", "redis"]})
    client_info.get_json("user")
    
    # JSON com path
    tags = client_info.get_json_path("user", '$.tags')
    print(f"Tags do usuário: {tags}")
    
    # Comandos de admin
    info = client_info.info()
    print(f"Versão Redis: {info.get('redis_version', 'N/A')}")
    
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
        fallback_enabled=True,
        retry_attempts=3
    )
    
    # Operações que geram warnings
    client_warning.flushall()  # Deve mostrar warning
    client_warning.delete("chave_inexistente")
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
        fallback_enabled=False,
        retry_attempts=1
    )
    
    try:
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
        fallback_enabled=True,
        retry_attempts=3
    )
    
    # Habilita métricas
    client_metrics.enable_metrics()
    
    # Executa operações variadas
    for i in range(5):
        client_metrics.set(f"metric:key:{i}", f"value{i}")
        client_metrics.get(f"metric:key:{i}")
    
    client_metrics.set_json("metric:json", {"counter": 0})
    client_metrics.incr("metric:counter")
    client_metrics.zadd("metric:zset", {"a": 1, "b": 2, "c": 3})
    
    # Mostra métricas
    metrics = client_metrics.get_metrics()
    print(f"Métricas coletadas: {len(metrics.get('commands', {}))} comandos")
    
    for cmd, data in metrics.get('commands', {}).items():
        print(f"  {cmd}: {data['count']} chamadas, média {data['avg_time_ms']}ms")
    
    # Limpeza
    for i in range(5):
        client_metrics.delete(f"metric:key:{i}")
    client_metrics.delete("metric:json", "metric:counter", "metric:zset")
    
    client_metrics.disable_metrics()
    client_metrics.close()

    print("\n" + "="*50)
    print("TESTE DE PUB/SUB")
    print("="*50 + "\n")
    
    client_pubsub = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="INFO",
        fallback_enabled=True
    )
    
    received = []
    
    def callback(channel, message):
        received.append((channel, message))
        print(f"📨 Recebido em {channel}: {message}")
    
    # Subscribe
    client_pubsub.subscribe("test:manual", callback)
    time.sleep(0.1)
    
    # Publish com nohistory
    client_pubsub.publish("test:manual", "Hello with nohistory!", nohistory=True)
    client_pubsub.publish_json("test:manual", {"type": "test", "data": "json message"})
    
    time.sleep(0.1)
    client_pubsub.close_pubsubs()
    client_pubsub.close()
    
    print(f"Mensagens recebidas: {len(received)}")

    print("\n" + "="*50)
    print("TESTE DE SORTED SET")
    print("="*50 + "\n")
    
    client_zset = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="DEBUG",
        fallback_enabled=True
    )
    
    # ZADD com opções
    client_zset.zadd("test:zset", {"a": 100, "b": 200, "c": 150})
    
    # ZRANGE avançado com BYSCORE
    results = client_zset.zrange("test:zset", 100, 200, byscore=True, withscores=True)
    print(f"ZRANGE BYSCORE: {results}")
    
    # ZMSCOPE
    scores = client_zset.zmscore("test:zset", ["a", "b", "c"])
    print(f"ZMSCOPE: {scores}")
    
    client_zset.delete("test:zset")
    client_zset.close()

    print("\n" + "="*50)
    print("TESTE DE JSON AVANÇADO")
    print("="*50 + "\n")
    
    client_json = RedisClient(
        host="localhost", 
        port=6379, 
        db=9, 
        log_level="DEBUG",
        fallback_enabled=True
    )
    
    # Criar JSON com array
    client_json.set_json("test:json:array", {
        'name': 'test',
        'tags': ['python', 'redis']
    })
    
    # Adicionar ao array
    client_json.arrappend_json("test:json:array", '$.tags', 'fastapi')
    length = client_json.arrlen_json("test:json:array", '$.tags')
    print(f"Tamanho do array: {length}")
    
    # Remover do array
    removed = client_json.arrpop_json("test:json:array", '$.tags')
    print(f"Removido do array: {removed}")
    
    client_json.delete("test:json:array")
    client_json.close()

    print("\n" + "="*50)
    print("✅ TESTES CONCLUÍDOS")
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
    
    # Usando URL com retry configurado
    client = RedisClient.from_url(
        "redis://localhost:6379/9",
        log_level="DEBUG",
        fallback_enabled=True,
        retry_attempts=5
    )
    
    client.set("url:test", "value")
    client.get("url:test")
    
    # JSON com URL
    client.set_json("url:user", {"name": "Test User", "tags": ["test"]})
    user = client.get_json("url:user")
    print(f"Usuário via URL: {user}")
    
    # JSON path
    client.set_json_path("url:user", '$.name', "Updated User")
    name = client.get_json_path("url:user", '$.name')
    print(f"Nome atualizado: {name}")
    
    client.delete("url:test", "url:user")
    client.close()


def test_retry_config():
    """Teste de configuração de retry"""
    
    print("\n" + "="*50)
    print("TESTE DE RETRY")
    print("="*50 + "\n")
    
    client = RedisClient(
        host="localhost",
        port=6379,
        db=9,
        log_level="INFO",
        retry_attempts=3
    )
    
    print(f"Retry attempts: {client.retry_attempts}")
    
    # Muda configuração de retry em runtime
    client.set_retry_attempts(5, backoff_base=2.0)
    print(f"Retry attempts alterado para: {client.retry_attempts}")
    
    client.close()


if __name__ == "__main__":
    test_manual_logging()
    test_from_url_logging()
    test_retry_config()