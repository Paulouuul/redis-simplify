import logging
import uuid
import time
from typing import Optional

logger = logging.getLogger('redis_simplify.client')

class LockMixin:
    """Lock distribuído usando Redis"""
    
    def lock(self, name: str, timeout: int = 10, blocking_timeout: Optional[int] = None):
        """Context manager para lock distribuído"""
        return RedisLock(self, name, timeout, blocking_timeout)


class RedisLock:
    def __init__(self, client, name: str, timeout: int, blocking_timeout: Optional[int]):
        self.client = client
        self.name = f"lock:{name}"
        self.timeout = timeout
        self.blocking_timeout = blocking_timeout
        self.token = None
    
    def __enter__(self):
        self.acquire()
        return self
    
    def acquire(self):
        if not self.client._ensure_connection():
            raise ConnectionError("Redis not connected")
        start = time.time()
        while True:
            self.token = str(uuid.uuid4())
            if self.client.set(self.name, self.token, self.timeout, nx=True):
                return True
            
            if self.blocking_timeout is None:
                continue
            
            if time.time() - start > self.blocking_timeout:
                raise TimeoutError(f"Could not acquire lock '{self.name}'")
            
            time.sleep(0.1)
    
    def __exit__(self, *args):
        if not self.client._ensure_connection():
            return
        # Release apenas se o token for o mesmo (Lua script para atomicidade)
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.client.client.eval(script, 1, self.name, self.token)