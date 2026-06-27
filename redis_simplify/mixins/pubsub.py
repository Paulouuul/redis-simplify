import logging
import threading
import json
import redis
from typing import Callable

from redis_simplify.mixins.decorator_metrics import recorded
from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class PubSubMixin:
    """Publicação e inscrição"""

    def __init__(self, *args, **kwargs):
        # Extrai argumentos específicos
        self._pubsubs = kwargs.pop('pubsubs', [])
        self._pubsub_threads = kwargs.pop('pubsub_threads', [])
        
        # Passa kwargs/args adiante (se houver)
        super().__init__(*args, **kwargs)

    @recorded()
    @with_fallback(default_return=0)
    def publish(self, channel: str, message: str) -> int:
        """Publica mensagem em canal"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.publish(channel, message)
    
    @with_fallback(default_return=0)
    def publish_json(self, channel: str, data: dict) -> int:
        """Publica JSON em canal"""
        return self.publish(channel, json.dumps(data))
    
    @with_fallback(default_return=None)
    def subscribe(self, channel: str, callback: Callable, pattern: bool = False):
        """Inscreve em canal com callback"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        pubsub = self.client.pubsub()
        
        if pattern:
            pubsub.psubscribe(channel)
        else:
            pubsub.subscribe(channel)
        
        # Variável para controlar o loop
        stop_event = threading.Event()
        
        def listener():
            try:
                for message in pubsub.listen():
                    if stop_event.is_set():
                        break
                    if message['type'] in ('message', 'pmessage'):
                        data = message.get('data')
                        channel_name = message.get('channel', message.get('pattern'))
                        callback(channel_name, data)
            except Exception as e:
                # Thread pode ser fechada normalmente
                logger.debug(f"PubSub listener stopped: {e}")
            finally:
                try:
                    pubsub.close()
                except:
                    pass
        
        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
        
        # Armazena para fechar depois
        self._pubsubs.append(pubsub)
        self._pubsub_threads.append((thread, pubsub, stop_event))
        
        logger.info(f"Subscribed to {channel}")
        return pubsub
    
    def close_pubsubs(self):
        """Fecha todas as subscriptions ativas"""
        for thread, pubsub, stop_event in self._pubsub_threads:
            stop_event.set()  # Sinaliza para parar
        
        # Aguarda threads terminarem
        for thread, pubsub, stop_event in self._pubsub_threads:
            try:
                if thread.is_alive():
                    thread.join(timeout=0.5)
            except:
                pass
        
        # Fecha pubsubs
        for pubsub in self._pubsubs:
            try:
                pubsub.close()
            except:
                pass
        
        self._pubsubs.clear()
        self._pubsub_threads.clear()