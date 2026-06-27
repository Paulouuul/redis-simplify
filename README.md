# redis-simplify

[![PyPI Version](https://img.shields.io/pypi/v/redis-simplify)](https://pypi.org/project/redis-simplify/)
[![Python Versions](https://img.shields.io/pypi/pyversions/redis-simplify)](https://pypi.org/project/redis-simplify/)
[![License](https://img.shields.io/pypi/l/redis-simplify)](LICENSE)
[![Downloads](https://pepy.tech/badge/redis-simplify)](https://pepy.tech/project/redis-simplify)
[![Tests](https://github.com/Paulouuul/redis-simplify/workflows/Tests/badge.svg)](https://github.com/Paulouuul/redis-simplify/actions)

**Redis made simple, safe, and production-ready.**

Stop writing boilerplate. Start building faster.

`redis-simplify` is a production-grade synchronous wrapper for Redis that eliminates repetitive code, handles connection failures automatically, and provides enterprise-ready features out of the box.

> Built on top of `redis-py`. Not a replacement — a force multiplier.

---
## Why redis-simplify?

| Problem | Solution |
|---|---|
|  Connection failures break your app | Automatic reconnection |
|  Endless try/except blocks | Built-in fallbacks |
|  No built-in monitoring | Metrics & health checks |
|  Boilerplate for caching | get_or_set() pattern |
|  Manual Redis admin | Info, slowlog, flush commands |
| No distributed locks | Built-in lock **context** manager |
|  No rate limiting | Sliding window rate limiter |
|  No async flush | Non-blocking flush operations |

**Stop fighting Redis. Start shipping.**

---

## Features

### Core Capabilities
- **Explicit configuration** — `host`, `port`, `password`, `db`
- **URL-based configuration** — `from_url()` for 12-factor apps
- **Automatic reconnection** — Self-healing connections
- **Centralized logging** — Configurable log levels
- **Safe fallback values** — Never crash on Redis errors
- **Lightweight** — Minimal overhead, maximum impact
- **Synchronous API** — Simple and predictable

### Enterprise Features
- **Distributed locks** — Context manager based
- **Rate limiting** — Sliding window algorithm
- **Cache utilities** — `get_or_set()`, `delete_pattern()`
- **Pub/Sub** — Callback-based subscriptions
- **Performance metrics** — Built-in decorators
- **Health checks** — Ready for monitoring
- **Batch operations** — Pipeline optimizations
- **Decorators** — `@cached`, `@retry`

### Data Structures
- **Strings** — Full string operations
- **JSON** — Native JSON serialization
- **Sorted Sets** — ZSET operations
- **Lists** — LPUSH, RPUSH, LRANGE
- **Sets** — SADD, SMEMBERS, SREM
- **Hashes** — HSET, HGET, HGETALL

### Admin & Monitoring
- **Server info** — `info()`, `info_sections()`
- **Slowlog** — Identify performance bottlenecks
- **DBSIZE** — Key count monitoring
- **Memory usage** — Per-key memory tracking
- **Client list** — Active connections
- **Flush operations** — Async/non-blocking

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

## Traditional parameters
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
# Or via URL (recommended for 12-factor apps)
```python
from redis_simplify import RedisClient

client = RedisClient.from_url(
    "redis://:password@localhost:6379/0",
    log_level="INFO"
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
| `incr(key)`                            | Increment a value       |
| `decr(key)`                            | Decrement a value       |
| `append(key, value)`                   | Append to a string      |
| `strlen(key)`                          | Get string length       |
| `getrange(key, start, end)`            | Get substring           |
| `setrange(key, offset, value)`         | Overwrite part of string|

---

### Keys

| Method                                      | Description                         |
| ------------------------------------------- | ----------------------------------- |
| `delete(*keys)`                             | Delete one or more keys             |
| `exists(key)`                               | Check if key exists                 |
| `expire(key, seconds)`                      | Set expiration in seconds           |
| `expireat(key, timestamp)`                  | Set expiration at Unix timestamp    |
| `ttl(key)`                                  | Get time to live in seconds         |
| `pttl(key)`                                 | Get time to live in milliseconds    |
| `persist(key)`                              | Remove expiration from key          |
| `rename(old_key, new_key)`                  | Rename a key                        |
| `renamenx(old_key, new_key)`                | Rename if new key doesn't exist     |
| `type(key)`                                 | Get key type                        |
| `keys(pattern="*")`                         | Get keys matching pattern (⚠️ use with caution) |
| `scan_iter(match=None, count=100)`          | Iterate keys without loading all    |
| `randomkey()`                               | Get random key from database        |

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

### Admin & Monitoring

| Method                          | Description                         |
| ------------------------------- | ----------------------------------- |
| `info(section=None)`            | Get Redis server information        |
| `info_sections()`               | List available info sections        |
| `dbsize()`                      | Get number of keys in current DB    |
| `memory_usage(key, samples=0)`  | Get memory usage of a key           |
| `slowlog(count=10)`             | Get slow queries log                |
| `client_list()`                 | List connected clients              |
| `flushdb(async_mode=False)`     | Clear current database              |
| `flushall(async_mode=False)`    | Clear all databases (careful!)      |

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

### Admin & Monitoring Examples

```python
# Get all server information
info = client.info()
print(f"Redis version: {info['redis_version']}")
print(f"Memory usage: {info['used_memory_human']}")

# Get specific section
memory_info = client.info('memory')
print(f"Memory fragmentation: {memory_info['mem_fragmentation_ratio']}")

# Check available sections
sections = client.info_sections()
print(f"Available sections: {sections}")

# Get database size
total_keys = client.dbsize()
print(f"Total keys: {total_keys}")

# Check memory usage of a specific key
usage = client.memory_usage("user:1")
print(f"Key memory usage: {usage} bytes")

# View slow queries
slow_commands = client.slowlog(5)
for cmd in slow_commands:
    print(f"Slow command: {cmd[3]} took {cmd[1]}ms")

# List connected clients
clients = client.client_list()
print(f"Connected clients: {len(clients)}")
```

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
| Memory monitoring   | Manual              | `memory_usage()`                   |
| Info sections       | No                  | `info_sections()`                  |
| Async flush         | Manual              | `flushdb(async_mode=True)`         |

---

## Best Practices

## Use `from_url()` for 12-factor apps

For cloud-native applications, use environment variables for configuration:

```python
import os
from redis_simplify import RedisClient

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
client = RedisClient.from_url(redis_url, log_level="INFO")
```

---

## Enable metrics for production monitoring

Monitor your Redis operations in production:

```python
client.enable_metrics()

# Your operations
for i in range(100):
    client.set(f"key:{i}", f"value:{i}")

# Get performance statistics
metrics = client.get_metrics()
print(f"Average SET time: {metrics['commands']['set']['avg_time_ms']}ms")
print(f"Total operations: {metrics['commands']['set']['count']}")

# Send metrics to monitoring system (Prometheus, Datadog, etc.)
send_to_monitoring(metrics)

# Reset when needed
client.reset_metrics()
```

---

## Use health checks for service monitoring

Implement health checks for your service:

```python
# In your health check endpoint
@app.route('/health')
def health():
    health = client.health_check()

    if health["status"] == "healthy":
        return {
            "status": "healthy",
            "redis": {
                "version": health["redis_version"],
                "memory": health["used_memory_human"],
                "clients": health["connected_clients"]
            }
        }, 200
    else:
        return {
            "status": "unhealthy",
            "error": health.get("error")
        }, 503
```

---

## Monitor slow queries in production

Keep an eye on performance issues:

```python
import time

def check_slow_queries():
    # Check for slow queries periodically
    slow = client.slowlog(10)

    if slow:
        logger.warning(f"Slow queries detected: {len(slow)}")
        for cmd in slow:
            # cmd = [id, timestamp, duration, command, ...]
            logger.warning(f"Slow command: {cmd[3]} took {cmd[1]}ms")

        # Alert your team or monitoring system
        alert_system(slow)

    return slow

# Run every minute
while True:
    check_slow_queries()
    time.sleep(60)
```

---

## Use context managers for pipelines

Ensure pipelines are properly executed:

```python
# Recommended - auto-executes on exit
with client.pipeline() as pipe:
    pipe.set("user:1", "John")
    pipe.set("user:2", "Jane")
    pipe.set("user:3", "Bob")
    # Auto-executes when exiting the context
```

```python
# Not recommended - manual execute (can be forgotten)
pipe = client.pipeline()
pipe.set("user:1", "John")
pipe.set("user:2", "Jane")
pipe.set("user:3", "Bob")
pipe.execute()  # Risk of forgetting this line
```

---

## Use distributed locks for critical sections

Prevent race conditions:

```python
# Recommended - automatic release with context manager
def process_payment(payment_id):
    with client.lock(f"payment:{payment_id}", timeout=10):
        # Critical section - only one instance executes
        payment = get_payment_from_db(payment_id)

        if payment.status == "pending":
            process_payment_logic(payment)
            update_payment_status(payment, "processed")
```

```python
# Not recommended - manual lock/unlock
def process_payment_manual(payment_id):
    lock_key = f"lock:payment:{payment_id}"

    if client.set(lock_key, "locked", nx=True, expire_seconds=10):
        try:
            process_payment_logic(payment)
        finally:
            client.delete(lock_key)
```

---

## Handle connection errors gracefully

Always check connectivity before critical operations:

```python
def get_user_data(user_id):
    # Check connection first
    if not client.ping():
        logger.error("Redis unavailable, falling back to database")
        return fetch_from_database(user_id)

    # Try cache first
    data = client.get(f"user:{user_id}")

    if data is None:
        data = fetch_from_database(user_id)
        client.set(f"user:{user_id}", data, expire_seconds=300)

    return data
```

---

## Use appropriate log levels

Configure logging based on environment:

```python
# Development
client = RedisClient(
    host="localhost",
    port=6379,
    log_level="DEBUG"
)

# Production
client = RedisClient(
    host="localhost",
    port=6379,
    log_level="INFO"
)

# High traffic
client = RedisClient(
    host="localhost",
    port=6379,
    log_level="ERROR"
)
```

---

## Reset metrics periodically

Prevent memory growth:

```python
import time

def collect_and_reset_metrics():
    while True:
        metrics = client.get_metrics()

        if metrics.get("enabled"):
            send_metrics_to_prometheus(metrics)
            client.reset_metrics()
            logger.info("Metrics collected and reset")

        time.sleep(3600)
```

---

## Use batch operations for multiple keys

Improve performance by reducing round trips:

```python
# Batch SET
items = [
    ("user:1", "John"),
    ("user:2", "Jane"),
    ("user:3", "Bob"),
    ("user:4", "Alice")
]

client.batch_set(items)

# Batch GET
keys = ["user:1", "user:2", "user:3", "user:4"]
users = client.batch_get(keys)
```

```python
# Multiple round trips
client.set("user:1", "John")
client.set("user:2", "Jane")
client.set("user:3", "Bob")
client.set("user:4", "Alice")

user1 = client.get("user:1")
user2 = client.get("user:2")
user3 = client.get("user:3")
user4 = client.get("user:4")
```

---

## Use SCAN instead of KEYS for large datasets

Avoid blocking Redis:

```python
# Recommended
def process_all_users():
    count = 0

    for key in client.scan_iter(match="user:*", count=100):
        data = client.get(key)
        process_user(data)

        count += 1

        if count % 1000 == 0:
            logger.info(f"Processed {count} users")

    return count
```

```python
# Dangerous
def process_all_users_dangerous():
    keys = client.keys("user:*")

    for key in keys:
        data = client.get(key)
        process_user(data)
```

---

## Use memory monitoring to detect issues

```python
def check_redis_memory():
    info = client.info("memory")

    used_memory = info["used_memory_human"]
    fragmentation = info["mem_fragmentation_ratio"]
    maxmemory = info.get("maxmemory_human", "0B")

    logger.info(
        f"Redis memory: used={used_memory}, max={maxmemory}"
    )

    if fragmentation > 1.5:
        logger.warning(
            f"High memory fragmentation: {fragmentation}"
        )

    for key in client.scan_iter(match="large:*", count=10):
        usage = client.memory_usage(key)

        if usage and usage > 10 * 1024 * 1024:
            logger.warning(
                f"Large key: {key} uses {usage} bytes"
            )
```

---

## Use Admin commands for debugging

```python
def debug_redis_connection():
    info = client.info()

    print(f"Redis version: {info['redis_version']}")
    print(f"Connected clients: {info['connected_clients']}")
    print(f"Keys in DB: {client.dbsize()}")

    slow = client.slowlog(10)

    if slow:
        print(f"Slow queries: {len(slow)}")

        for cmd in slow:
            print(f"  {cmd[3]} - {cmd[1]}ms")

    clients = client.client_list()

    print(f"Active clients: {len(clients)}")

    for c in clients[:5]:
        print(f"  {c.get('addr')} - {c.get('age')}s")
```

---

## Use cache patterns effectively

```python
def get_user_profile(user_id):
    return client.get_or_set(
        f"user:{user_id}:profile",
        lambda: fetch_user_from_database(user_id),
        ttl=300
    )

def get_user_with_fallback(user_id):
    data = client.get(f"user:{user_id}")

    if data is None:
        data = fetch_from_database(user_id)
        client.set(
            f"user:{user_id}",
            data,
            expire_seconds=3600
        )

    return data

def invalidate_user_cache(user_id):
    client.delete(f"user:{user_id}")
    client.delete_pattern(f"user:{user_id}:*")
```

---

## Use rate limiting to protect APIs

```python
def api_endpoint(user_id):
    if not client.rate_limit_check(
        f"api:user:{user_id}",
        10,
        60
    ):
        return {"error": "Rate limit exceeded"}, 429

    data = client.get_or_set(
        f"api:data:{user_id}",
        lambda: expensive_computation(user_id),
        ttl=60
    )

    return {"data": data}, 200
```

```python
def api_endpoint_simple(user_id):
    data = client.run_with_rate_limit(
        client.get,
        f"api:user:{user_id}",
        10,
        60,
        f"user:{user_id}"
    )

    if data is None:
        return {"error": "Rate limit exceeded"}, 429

    return {"data": data}, 200
```

---

## Use Pub/Sub for real-time notifications

```python
def setup_notification_handlers():

    def handle_order_update(channel, message):
        order_id = json.loads(message)["order_id"]
        logger.info(f"Order {order_id} updated")
        process_order_update(order_id)

    def handle_user_message(channel, message):
        user_id = json.loads(message)["user_id"]
        logger.info(f"Message for user {user_id}")
        send_push_notification(user_id, message)

    client.subscribe("orders", handle_order_update)
    client.subscribe("notifications", handle_user_message)
    client.subscribe("messages", handle_user_message)

def notify_order_update(order_id, status):
    client.publish_json(
        "orders",
        {
            "order_id": order_id,
            "status": status,
            "timestamp": time.time()
        }
    )
```

---

## Use proper cleanup when using context managers

```python
# Automatic cleanup
with client as c:
    c.set("key", "value")
    data = c.get("key")
```

```python
# Pipeline with auto execute
with client.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
```

```python
# Manual cleanup
try:
    client.pipeline()
finally:
    client.close()
```

---

## Use decorators for common patterns

```python
@client.cached(ttl=60, key_prefix="db")
def get_expensive_data(query_id):
    return expensive_database_query(query_id)

@client.retry(max_attempts=3, delay=0.5)
def call_external_api(url):
    return requests.get(url, timeout=5)

@client.cached(ttl=300)
@client.retry(max_attempts=3)
def get_external_data_with_retry(endpoint):
    return fetch_from_external_api(endpoint)
```

---

## Use info sections for targeted monitoring

```python
def monitor_redis():
    memory = client.info("memory")
    stats = client.info("stats")
    clients = client.info("clients")
    replication = client.info("replication")

    return {
        "memory_used": memory["used_memory_human"],
        "memory_fragmentation": memory["mem_fragmentation_ratio"],
        "ops_per_second": stats["instantaneous_ops_per_sec"],
        "connected_clients": clients["connected_clients"],
        "role": replication["role"]
    }
```

---

## Use async flush for non-blocking operations

```python
# Recommended
client.flushdb(async_mode=True)
logger.info("Database flush initiated (async)")

while True:
    info = client.info("persistence")

    if info["rdb_bgsave_in_progress"] == 0:
        break

    time.sleep(1)
```

```python
# Not recommended
client.flushdb()
```

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

## 💖 Support the Project

If you find this project useful:
- ⭐ Star the repository
- 🔧 Contribute code or documentation
- 📢 Share with your network
- 💰 Consider sponsoring
