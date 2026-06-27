import logging
import traceback
import uuid
import time
import redis
from typing import Optional

from redis_simplify.mixins.decorators import with_fallback

logger = logging.getLogger('redis_simplify.client')

class LockMixin:
    """Lock distribuído usando Redis"""
    
    @with_fallback(default_return=None)
    def lock(self, name: str, timeout: int = 10, blocking_timeout: Optional[int] = None):
        """Context manager para lock distribuído"""
        if not self._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        return RedisLock(self, name, timeout, blocking_timeout)


class RedisLock:
    def __init__(self, client, name: str, timeout: int, blocking_timeout: Optional[int]):
        self.client = client
        self.name = f"lock:{name}"
        self.timeout = timeout
        self.blocking_timeout = blocking_timeout
        self.token = None
        self.acquired = False
    
    def __enter__(self):
        self.acquire()
        return self
    
    @with_fallback(default_return=False)
    def acquire(self):
        """Adquire o lock"""
        if not self.client._ensure_connection():
            raise redis.ConnectionError("Redis connection failed")
        
        start = time.time()
        while True:
            self.token = str(uuid.uuid4())
            if self.client.set(self.name, self.token, self.timeout, nx=True):
                self.acquired = True
                return True
            
            if self.blocking_timeout is None:
                continue
            
            if time.time() - start > self.blocking_timeout:
                raise TimeoutError(f"Could not acquire lock '{self.name}'")
            
            time.sleep(0.1)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Error on lock: {exc_type.__name__}: {exc_val}")
            logger.error(f"Traceback: {''.join(traceback.format_tb(exc_tb))}")
        
        if not self.acquired:
            return False
        
        if not self.client._ensure_connection():
            logger.error("Redis connection failed while releasing lock")
            return False
        
        # Script Lua para liberar o lock de forma segura
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            self.client.client.eval(script, 1, self.name, self.token)
        except Exception as e:
            logger.error(f"Error releasing lock '{self.name}': {e}")
            return False
        
        return None