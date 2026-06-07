import logging
import threading
from typing import Callable

from redis_simplify.mixins.decorator_metrics import recorded

logger = logging.getLogger('redis_simplify.client')

class PubSubMixin:
    """Publicação e inscrição"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pubsubs = []  # Armazena subscriptions ativas
        self._pubsub_threads = []  # Armazena threads ativas

    @recorded()
    def publish(self, channel: str, message: str) -> int:
        """Publica mensagem em canal"""
        if not self._ensure_connection():
            return 0
        try:
            return self.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Error on publish {channel}: {e}")
            return 0
    
    def publish_json(self, channel: str, data: dict) -> int:
        """Publica JSON em canal"""
        import json
        return self.publish(channel, json.dumps(data))
    
    def subscribe(self, channel: str, callback: Callable, pattern: bool = False):
        """Inscreve em canal com callback"""
        if not self._ensure_connection():
            logger.error("Cannot subscribe: no Redis connection")
            return None
        
        pubsub = self.client.pubsub()
        
        if pattern:
            pubsub.psubscribe(channel)
        else:
            pubsub.subscribe(channel)
        
        # Flag para controlar o loop
        running = True
        
        def listener():
            try:
                for message in pubsub.listen():
                    if not running:
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
        self._pubsub_threads.append((thread, pubsub, lambda: running))
        
        logger.info(f"Subscribed to {channel}")
        return pubsub
    
    def close_pubsubs(self):
        """Fecha todas as subscriptions ativas"""
        for pubsub in self._pubsubs:
            try:
                pubsub.close()
            except:
                pass
        self._pubsubs.clear()
        
        # Aguarda threads terminarem
        for thread, pubsub, _ in self._pubsub_threads:
            try:
                if thread.is_alive():
                    thread.join(timeout=0.5)
            except:
                pass
        self._pubsub_threads.clear()