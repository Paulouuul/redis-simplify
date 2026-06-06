## Configuration

All configuration is explicit via constructor parameters:

```python
from redis_simplify import RedisClient

client = RedisClient(
    host="localhost",   # Required
    port=6379,          # Default: 6379
    password=None,      # Optional
    db=0                # Default: 0
)
```

The package does not automatically read `.env` files.

Configuration is intentionally explicit to keep behavior predictable and framework-agnostic.

---

## Automatic Reconnection Example

```python
from redis_simplify import RedisClient

# Redis is running
client = RedisClient(host="localhost")

client.set("key", "value")  # ✅ Works

# Redis goes down
# ... server restart, network interruption, etc.

# When Redis becomes available again,
# the next operation automatically attempts reconnection.

value = client.get("key")

print(value)
```

No manual reconnection logic is required.

---

## Differences from redis-py

| Feature             | redis-py            | redis-simplify                     |
| ------------------- | ------------------- | ---------------------------------- |
| Exception handling  | Raises exceptions   | Logs and returns fallback values   |
| Reconnection        | Manual handling     | Automatic                          |
| JSON helpers        | No built-in helpers | `set_json()` / `get_json()`        |
| Configuration       | Highly flexible     | Explicit constructor configuration |
| Convenience wrapper | No                  | Yes                                |
| Safe defaults       | No                  | Yes                                |

---

## Documentation

Useful resources:

* Redis Commands: https://redis.io/commands
* redis-py Documentation: https://redis-py.readthedocs.io/
* redis-simplify GitHub: https://github.com/Paulouuul/redis-simplify