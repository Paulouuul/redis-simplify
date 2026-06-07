import logging
import threading
from typing import Callable

from redis_simplify.mixins.metrics import MetricsMixin
logger = logging.getLogger('redis_simplify.client')

class PubSubMixin:
    """Publicação e inscrição simplificadas"""
    @MetricsMixin._recorded
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
        if not self._ensure_connection():
            logger.error("Cannot subscribe: no Redis connection")
            return None
        """Inscreve em canal com callback"""
        pubsub = self.client.pubsub()
        
        if pattern:
            pubsub.psubscribe(channel)
        else:
            pubsub.subscribe(channel)
        
        def listener():
            for message in pubsub.listen():
                if message['type'] in ('message', 'pmessage'):
                    data = message.get('data')
                    channel_name = message.get('channel', message.get('pattern'))
                    callback(channel_name, data)
        
        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
        logger.info(f"Subscribed to {channel}")
        return pubsub