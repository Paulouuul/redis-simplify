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
* Support for the most commonly used Redis operations:

  * Strings
  * Sets
  * Hashes
  * Lists
  * Pipelines
  * SCAN iteration

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
| `set(key, value, expire_seconds=None)` | Set a value             |
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

### Utilities

| Method                                   | Description                |
| ---------------------------------------- | -------------------------- |
| `ping()`                                 | Verify connectivity        |
| `pipeline()`                             | Create a Redis pipeline    |
| `scan(cursor=0, match=None, count=None)` | Iterate keys using SCAN    |
| `flush_all()`                            | Remove all Redis databases |
| `close()`                                | Close the connection       |
| `set_log_level(level)`                   | Change log level at runtime|

---

## Pipeline Example

```python
pipe = client.pipeline()

pipe.set("user:1", "John")
pipe.set("user:2", "Jane")

pipe.execute()
```

---

## SCAN Example

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

---

## Running Tests

The project includes automated tests built with `pytest`.

```bash
pytest
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
