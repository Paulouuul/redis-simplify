# redis-simplify

[![PyPI Version](https://img.shields.io/pypi/v/redis-simplify)](https://pypi.org/project/redis-simplify/)
[![Python Versions](https://img.shields.io/pypi/pyversions/redis-simplify)](https://pypi.org/project/redis-simplify/)
[![License](https://img.shields.io/pypi/l/redis-simplify)](LICENSE)

A lightweight synchronous convenience wrapper for Redis built on top of **redis-py**.

`redis-simplify` was created to reduce repetitive Redis boilerplate in Python applications by providing a simple and consistent interface with automatic reconnection, JSON helpers, centralized logging, and defensive error handling.

> This package is not a Redis client replacement. It is a convenience layer built on top of `redis-py` to simplify common Redis operations.

---

## Features

* Explicit Redis configuration (`host`, `port`, `password`, `db`)
* Automatic reconnection when Redis becomes unavailable
* Centralized logging and error handling
* JSON helpers for storing Python dictionaries
* Safe fallback values on failures
* Fully tested with `pytest`
* Lightweight implementation
* Synchronous API
* **18 specialized mixins** for organized code
* **Distributed locks** with context manager
* **Rate limiting** utilities
* **Cache utilities** (get_or_set, delete_pattern)
* **Pub/Sub** simplified
* **Performance metrics** collection
* **Health checks** and monitoring
* **Batch operations** support
* **Decorators** for caching and retry
* Support for **Sorted Sets**, **Hashes**, **Lists**, **Sets**, **Strings**

---

## Installation

### Basic Installation

```bash
pip install redis-simplify
```

### With Test Dependencies (Contributors)

```bash
pip install redis-simplify[test]
```

### Full Development Setup

```bash
git clone https://github.com/Paulouuul/redis-simplify
cd redis-simplify

pip install -e .[dev]

pytest tests/ -v
```

---

## Requirements

* Python >= 3.8
* redis-py >= 4.0.0

---

## Quick Start

```python
from redis_simplify import RedisClient

client = RedisClient(
    host="localhost",
    port=6379
)
```

---

## Configuration

All configuration is explicit via constructor parameters:

```python
from redis_simplify import RedisClient

client = RedisClient(
    host="localhost",   # Required
    port=6379,          # Default: 6379
    password=None,      # Optional
    db=0,               # Default: 0
    log_level=None      # Default: None (inherits from root logger)
)
```

Configuration is intentionally explicit to keep behavior predictable and framework-agnostic.

---

## Basic Usage

### Strings

```python
from redis_simplify import RedisClient

client = RedisClient(host="localhost", port=6379)

client.set("chave", "valor")

print(client.get("chave"))
```

Output:

```python
valor
```

---

### JSON Helpers

Store Python dictionaries directly in Redis.

```python
client.set_json(
    "usuario:1",
    {
        "nome": "João",
        "idade": 30
    }
)

print(client.get_json("usuario:1"))
```

Output:

```python
{
    "nome": "João",
    "idade": 30
}
```

---

### Sets

```python
client.sadd("tags", "python", "redis")

print(client.smembers("tags"))
```

Possible output:

```python
{"python", "redis"}
```

---

### Connection Check

```python
if client.ping():
    print("Redis online")
else:
    print("Redis unavailable")
```

---

## Automatic Reconnection

Before executing operations, the client verifies the connection status.

If Redis becomes unavailable, the wrapper automatically attempts to reconnect before executing the requested command.

This behavior is transparent to application code and helps reduce connection-management boilerplate.

---

## Automatic Reconnection Example

```python
from redis_simplify import RedisClient

# Redis is running
client = RedisClient(host="localhost")

client.set("key", "value")

# Redis goes down...
# server restart, network interruption, etc.

# When Redis becomes available again,
# the next operation automatically attempts reconnection

value = client.get("key")

print(value)
```

No manual reconnection logic is required.

---

## Error Handling

All operations include consistent exception handling and logging.

Instead of propagating Redis exceptions, the wrapper logs errors and returns safe fallback values whenever possible.

### Fallback Values

When Redis operations fail, the wrapper returns safe defaults instead of raising exceptions:

| Return Type    | Fallback |
| -------------- | -------- |
| `str` / object | `None`   |
| `bool`         | `False`  |
| `int`          | `0`      |
| `list`         | `[]`     |
| `dict`         | `{}`     |
| `set`          | `set()`  |

This approach helps keep application code clean and reduces repetitive `try/except` blocks.

---

## Logging

The client uses Python's built-in `logging` module. 

By default (`log_level=None`), the logger inherits the level from the root logger 
(usually `WARNING`). You can override this by setting `log_level` or using `set_log_level()`.

### Configuring Log Level

```python
# Set during initialization
client = RedisClient(host="localhost", log_level="DEBUG")

# Or change after creation
client.set_log_level("WARNING")
```
### Log 

| Level     | Shows                                  |
|-----------|----------------------------------------|
|`DEBUG`    | All operations (set, get, delete, etc.)|
| `INFO`    | Connections and errors                 |
| `WARNING` | Warnings and errors only               |
| `ERROR`   | Errors only                            |

## Example Output with DEBUG

```bash
INFO:redis_simplify.client:RedisClient connected: localhost:6379
DEBUG:redis_simplify.client:Set test = hello world...
DEBUG:redis_simplify.client:Get test: hello world...
```

## Available Methods

### Strings

| Method                                 | Description             |
| -------------------------------------- | ----------------------- |
| `set(key, value, expire_seconds=None, nx=False, xx=False)` | Set a value with options |
| `get(key)`                             | Retrieve a value        |
| `delete(*keys)`                        | Delete one or more keys |
| `exists(key)`                          | Check if a key exists   |
| `expire(key, seconds)`                 | Set expiration time     |
| `incr(key)`                            | Increment a value       |
| `decr(key)`                            | Decrement a value       |

---

### JSON

| Method                                     | Description                   |
| ------------------------------------------ | ----------------------------- |
| `set_json(key, data, expire_seconds=None)` | Store a dictionary as JSON    |
| `get_json(key)`                            | Retrieve and deserialize JSON |

---

### Sets

| Method                  | Description          |
| ----------------------- | -------------------- |
| `sadd(key, *values)`    | Add members          |
| `srem(key, *values)`    | Remove members       |
| `smembers(key)`         | Retrieve all members |
| `sismember(key, value)` | Check membership     |
| `scard(key)`            | Count members        |

---

### Hashes

| Method                    | Description         |
| ------------------------- | ------------------- |
| `hset(key, field, value)` | Set a hash field    |
| `hget(key, field)`        | Retrieve a field    |
| `hgetall(key)`            | Retrieve all fields |

---

### Lists

| Method                    | Description                  |
| ------------------------- | ---------------------------- |
| `lpush(key, *values)`     | Push values to the beginning |
| `rpush(key, *values)`     | Push values to the end       |
| `lrange(key, start, end)` | Retrieve a range of values   |

---
### Sorted Sets (ZSET)
| Method                                      | Description                    |
| ------------------------------------------- | ------------------------------ |
| `zadd(key, mapping)`                        | Add members with scores        |
| `zrange(key, start, stop, withscores=False)`| Retrieve members by rank        |
| `zrevrange(key, start, stop, withscores=False)` | Retrieve members in reverse |
| `zrank(key, member)`                        | Get member rank                |
| `zscore(key, member)`                       | Get member score               |
| `zincrby(key, amount, member)`              | Increment member score         |
| `zrem(key, *members)`                       | Remove members                 |
| `zcard(key)`                                | Get member count               |

### Cache Utilities
| Method                                          | Description                         |
| ----------------------------------------------- | ----------------------------------- |
| `get_or_set(key, func, ttl=None)`               | Get from cache or set from function |
| `get_or_set_json(key, func, ttl=None)`          | JSON version of get_or_set          |
| `delete_pattern(pattern, batch_size=1000)`      | Delete all keys matching pattern    |
| `scan_iter(match=None, count=100)`              | Iterate keys without loading all    |

### Rate Limiting
| Method                                                  | Description                       |
| ------------------------------------------------------- | --------------------------------- |
| `rate_limit_check(key, max_requests, window_seconds)`   | Check if action is allowed        |
| `rate_limit_remaining(key, max_requests, window_seconds)` | Get remaining requests          |
| `rate_limit_reset(key, window_seconds)`                 | Get seconds until reset           |
| `run_with_rate_limit(operation, rate_key, max_requests, window_seconds, *args, **kwargs)` | Execute operation with automatic rate limit |

### Distributed Lock
| Method                                      | Description                         |
| ------------------------------------------- | ----------------------------------- |
| `lock(name, timeout=10, blocking_timeout=None)` | Context manager for distributed lock |

### Pub/Sub
| Method                                      | Description                         |
| ------------------------------------------- | ----------------------------------- |
| `publish(channel, message)`                 | Publish message to channel          |
| `publish_json(channel, data)`               | Publish JSON to channel             |
| `subscribe(channel, callback, pattern=False)` | Subscribe to channel with callback |

### Batch Operations
| Method                                      | Description                         |
| ------------------------------------------- | ----------------------------------- |
| `batch_get(keys)`                           | Get multiple keys via pipeline      |
| `batch_set(items, expire_seconds=None)`     | Set multiple keys via pipeline      |
| `batch_delete(keys)`                        | Delete multiple keys via pipeline   |

### Utils
| Method                                          | Description                         |
| ----------------------------------------------- | ----------------------------------- |
| `mget(keys)`                                    | Get multiple keys at once           |
| `mset(mapping, expire_seconds=None)`            | Set multiple keys at once           |
| `rename_safe(old_key, new_key, overwrite=False)`| Rename with safety check            |
| `copy_key(source, destination, replace=False)`  | Copy key to another location        |

### Health & Metrics
| Method                          | Description                         |
| ------------------------------- | ----------------------------------- |
| `health_check()`                | Check Redis server health           |
| `ping_latency(count=10)`        | Measure ping latency                |
| `enable_metrics()`              | Start collecting performance metrics|
| `get_metrics()`                 | Retrieve collected metrics          |
| `reset_metrics()`               | Reset all metrics                   |

### Decorators
| Method                                      | Description                         |
| ------------------------------------------- | ----------------------------------- |
| `@cached(ttl=300, key_prefix="")`           | Automatic caching decorator         |
| `@retry(max_attempts=3, delay=0.5)`         | Retry with exponential backoff      |

### Utilities

| Method                                   | Description                |
| ---------------------------------------- | -------------------------- |
| `ping()`                                 | Verify connectivity        |
| `pipeline()`                             | Create a Redis pipeline    |
| `scan(cursor=0, match=None, count=None)` | Iterate keys using SCAN    |
| `flushall()`                             | Remove all Redis databases |
| `close()`                                | Close the connection       |
| `set_log_level(level)`                   | Change log level at runtime|

---
## Examples
### Pipeline Example

```python
pipe = client.pipeline()

pipe.set("user:1", "John")
pipe.set("user:2", "Jane")

pipe.execute()
```

---

### SCAN Example

```python
cursor = 0

while True:
    cursor, keys = client.scan(
        cursor=cursor,
        match="user:*",
        count=100
    )

    print(keys)

    if cursor == 0:
        break
```

---
### Advanced Examples

#### Distributed Lock

```python
# Ensure only one instance executes a critical section
with client.lock("payment_processing", timeout=10):
    process_payment()
    # Lock automatically released after the block
```
#### Rate Limiting

##### Manual check
```python
if client.rate_limit_check(f"api:user:{user_id}", 10, 60):
    data = client.get(f"user:{user_id}")
```

#### Automatic with run_with_rate_limit (simpler!)
```python
data = client.run_with_rate_limit(
    client.get, f"api:user:{user_id}", 10, 60,
    f"user:{user_id}"
)
if data is None:
    return {"error": "Rate limit exceeded"}, 429
```
#### Cache Pattern (Get or Set)

```python
def get_user_profile(user_id):
    # Returns cached value or computes and stores it
    return client.get_or_set(
        f"user:{user_id}",
        lambda: fetch_user_from_database(user_id),
        ttl=300  # 5 minutes
    )
```
#### Delete Pattern
```python
# Delete all session keys for a user
client.delete_pattern("session:user:123:*")
```
#### SCAN Iterator (Memory Efficient)
```python
# Iterate through keys without loading all into memory
for key in client.scan_iter(match="user:*", count=100):
    print(key, client.get(key))
```
#### Batch Operations
```python
# Set multiple keys efficiently
items = [("user:1", "John"), ("user:2", "Jane"), ("user:3", "Bob")]
client.batch_set(items)

# Get multiple keys at once
result = client.batch_get(["user:1", "user:2", "user:3"])
```
#### Pub/Sub Messaging
``` python
def message_handler(channel, message):
    print(f"Received on {channel}: {message}")

# Subscribe to a channel
client.subscribe("notifications", message_handler)

# Publish messages
client.publish("notifications", "Hello subscribers!")
```
### Health Check
```python
health = client.health_check()
if health["status"] == "healthy":
    print(f"Redis {health['redis_version']} running")
    print(f"Memory usage: {health['used_memory_human']}")
    print(f"Connected clients: {health['connected_clients']}")
```
#### Performance Metrics
```python
client.enable_metrics()

# Execute your operations
for i in range(100):
    client.set(f"key:{i}", f"value:{i}")

# Get performance statistics
metrics = client.get_metrics()
print(f"Average SET time: {metrics['commands']['set']['avg_time_ms']}ms")
print(f"Total operations: {metrics['commands']['set']['count']}")

client.reset_metrics()  # Clear metrics when needed
```
#### Decorator Pattern
```python
@client.cached(ttl=60)
def expensive_database_query(user_id):
    # This will be cached automatically
    return database.fetch_user(user_id)

@client.retry(max_attempts=3, delay=0.5)
def unstable_network_call():
    # Automatically retries up to 3 times on failure
    return external_api.call()
```
#### Pipeline with Context Manager
```python
# Auto-executes when exiting the context
with client.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.incr("counter")
```
#### Multiple Operations with mget/mset
```python
# Set multiple keys
client.mset({"user:1": "John", "user:2": "Jane", "user:3": "Bob"})

# Get multiple keys
users = client.mget(["user:1", "user:2", "user:3"])
print(users)  # {"user:1": "John", "user:2": "Jane", "user:3": "Bob"}
```

## Shared Instance Pattern

`redis-simplify` does not enforce a Singleton pattern.

However, many applications create a single shared instance and reuse it throughout the project:

```python
from redis_simplify import RedisClient

redis_client = RedisClient(
    host="localhost",
    port=6379
)
```

---

## Why redis-simplify?

Many projects repeatedly implement:

* Redis connection setup
* Health checks
* Reconnection logic
* JSON serialization and deserialization
* Logging
* Defensive exception handling

`redis-simplify` centralizes these concerns into a small reusable wrapper while preserving the familiar Redis workflow provided by `redis-py`.

---

## Differences from redis-py

| Feature             | redis-py            | redis-simplify                     |
| ------------------- | ------------------- | ---------------------------------- |
| Exception handling  | Raises exceptions   | Logs and returns fallback values   |
| Reconnection        | Manual handling     | Automatic                          |
| JSON helpers        | No built-in helpers | `set_json()` / `get_json()`        |
| Configuration       | Highly flexible     | Explicit constructor configuration |
| Logging control     | Basic               | Configurable log levels            |
| Convenience wrapper | No                  | Yes                                |
| Safe defaults       | No                  | Yes                                |
| Distributed locks   | Manual (SET NX)     | Built-in with context manager      |
| Rate limiting       | No                  | Built-in sliding window            |
| Performance metrics | No                  | Built-in with decorators           |
| Health checks       | Manual (INFO)       | Built-in `health_check()`          |
| Cache patterns      | Manual              | `get_or_set()`, `delete_pattern()` |
| Batch operations    | Manual pipeline     | `batch_get()`, `batch_set()`       |
| Decorators          | No                  | `@cached`, `@retry`                |
| Pub/Sub simplified  | Manual              | Callback-based subscription        |

---

## Running Tests

The project includes automated tests built with `pytest`.

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test categories
```bash
# Run only string operations tests
pytest tests/test_client.py::TestRedisClientString -v

# Run only JSON tests
pytest tests/test_client.py::TestRedisClientJSON -v

# Run only metrics tests
pytest tests/test_client.py::TestRedisClientMetrics -v

# Run only lock tests
pytest tests/test_client.py::TestRedisClientLock -v
```

---

## Contributing

Contributions are welcome.

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add or update tests when applicable
5. Open a Pull Request

Bug reports, improvements, and feature suggestions are appreciated.

---

## Documentation

Useful resources:

* Redis Commands: https://redis.io/commands
* redis-py Documentation: https://redis.readthedocs.io/en/latest/
* redis-simplify GitHub: https://github.com/Paulouuul/redis-simplify

---

## License

This project is licensed under the MIT License.

---

## Author

**Paulo Ricardo Tebet Lyrio**

GitHub: https://github.com/Paulouuul/redis-simplify
