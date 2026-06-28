import logging
import threading
import json
import redis
from typing import Callable, Optional, List, Dict, Any, Union

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

    # ============ PUBLISH ============
    
    @recorded()
    @with_fallback(default_return=0)
    def publish(self, channel: str, message: str, nohistory: bool = False) -> int:
        """
        Publica mensagem em canal.
        
        Args:
            channel: Nome do canal
            message: Mensagem a ser publicada
            nohistory: Não armazena histórico da mensagem (Redis 8.0+)
        
        Returns:
            int: Número de subscribers que receberam a mensagem
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.publish(channel, message, nohistory=nohistory)
    
    @with_fallback(default_return=0)
    def publish_json(self, channel: str, data: dict, nohistory: bool = False) -> int:
        """Publica JSON em canal"""
        return self.publish(channel, json.dumps(data), nohistory=nohistory)
    
    # ============ SUBSCRIBE ============
    
    @with_fallback(default_return=None)
    def subscribe(self, channel: str, callback: Callable, pattern: bool = False):
        """
        Inscreve em canal com callback.
        
        Args:
            channel: Nome do canal ou padrão
            callback: Função a ser chamada ao receber mensagem
            pattern: Se True, usa psubscribe (padrão)
        """
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
    
    # ============ UNSUBSCRIBE ============
    
    @with_fallback(default_return=False)
    def unsubscribe(self, channel: Optional[str] = None):
        """
        Cancela inscrição em canal.
        
        Args:
            channel: Canal a取消 (None = todos)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        # Encontra e para a thread correspondente
        for i, (thread, pubsub, stop_event) in enumerate(self._pubsub_threads):
            if channel is None or self._get_channel_from_pubsub(pubsub) == channel:
                stop_event.set()
                thread.join(timeout=1.0)
                try:
                    pubsub.unsubscribe()
                except:
                    pass
                self._pubsub_threads.pop(i)
                self._pubsubs.pop(i)
                logger.info(f"Unsubscribed from {channel or 'all'}")
                return True
        return False
    
    def _get_channel_from_pubsub(self, pubsub) -> Optional[str]:
        """Obtém o canal de um pubsub (auxiliar)"""
        try:
            if hasattr(pubsub, 'channels'):
                return list(pubsub.channels.keys())[0] if pubsub.channels else None
            return None
        except:
            return None
    
    # ============ PUBSUB COMMANDS ============
    
    @with_fallback(default_return=[])
    def pubsub_channels(self, pattern: Optional[str] = None) -> List[str]:
        """
        Lista canais ativos (Redis 2.8+).
        
        Args:
            pattern: Padrão para filtrar canais (opcional)
        
        Returns:
            Lista de canais ativos
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.pubsub_channels(pattern=pattern)
    
    @with_fallback(default_return=0)
    def pubsub_numsub(self, *channels: str) -> List[tuple]:
        """
        Retorna número de subscribers por canal (Redis 2.8+).
        
        Returns:
            Lista de tuplas (canal, subscribers)
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.pubsub_numsub(*channels)
    
    @with_fallback(default_return=0)
    def pubsub_numpat(self) -> int:
        """
        Retorna número de subscriptions com padrão (Redis 2.8+).
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.pubsub_numpat()
    
    # ============ PUBSUB SHARDED ============
    
    @recorded()
    @with_fallback(default_return=0)
    def spublish(self, channel: str, message: str) -> int:
        """
        Publica em canal sharded (Redis 7.0+).
        
        Args:
            channel: Nome do canal
            message: Mensagem a ser publicada
        
        Returns:
            int: Número de subscribers sharded
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return self.client.spublish(channel, message)
    
    @with_fallback(default_return=None)
    def ssubscribe(self, channel: str, callback: Callable):
        """
        Inscreve em canal sharded com callback (Redis 7.0+).
        """
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        pubsub = self.client.pubsub()
        pubsub.ssubscribe(channel)
        
        stop_event = threading.Event()
        
        def listener():
            try:
                for message in pubsub.listen():
                    if stop_event.is_set():
                        break
                    if message['type'] in ('message', 'smessage'):
                        data = message.get('data')
                        channel_name = message.get('channel')
                        callback(channel_name, data)
            except Exception as e:
                logger.debug(f"Sharded PubSub listener stopped: {e}")
            finally:
                try:
                    pubsub.close()
                except:
                    pass
        
        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
        
        self._pubsubs.append(pubsub)
        self._pubsub_threads.append((thread, pubsub, stop_event))
        
        logger.info(f"Subscribed to sharded channel {channel}")
        return pubsub
    
    # ============ GESTÃO ============
    
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
        logger.info("All PubSub connections closed")
    
    def get_active_subscriptions(self) -> int:
        """Retorna número de subscriptions ativas"""
        return len(self._pubsub_threads)
    
    def get_active_channels(self) -> List[str]:
        """Retorna lista de canais ativos"""
        channels = []
        for pubsub in self._pubsubs:
            try:
                if hasattr(pubsub, 'channels'):
                    channels.extend(pubsub.channels.keys())
            except:
                pass
        return channels