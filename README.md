# async-cache
> A high-performance async caching solution for Python

[![PyPI version](https://img.shields.io/pypi/v/async-cache.svg)](https://pypi.python.org/pypi/async-cache)
[![Downloads](https://static.pepy.tech/personalized-badge/async-cache?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/async-cache)
[![Security Rating](https://snyk.io/advisor/python/async-cache/badge.svg)](https://snyk.io/advisor/python/async-cache)

A lightweight, efficient caching solution designed specifically for asyncio applications. Supports both LRU (Least Recently Used) and TTL (Time To Live) caching strategies with a clean, decorator-based API.

## Features

- 🚀 **Async-First**: Built specifically for asyncio applications
- 🔄 **Multiple Cache Types**: 
  - LRU (Least Recently Used) cache
  - TTL (Time To Live) cache
- 🎯 **Flexible Key Generation**: Works with primitive types, custom objects, and ORM models
- 🛠 **Configurable**: Adjustable cache size and TTL duration
- 🧹 **Cache Management**: Clear cache on demand
- 💡 **Smart Argument Handling**: Skip specific arguments in cache key generation
- 🔍 **Cache Bypass**: Ability to bypass cache for specific calls

## Installation

```bash
pip install async-cache
```

## Basic Usage

### LRU Cache

The LRU cache maintains a fixed number of items, removing the least recently used item when the cache is full.

```python
from cache import AsyncLRU

@AsyncLRU(maxsize=128)
async def get_user_data(user_id: int) -> dict:
    # Expensive database operation
    data = await db.fetch_user(user_id)
    return data
```

### TTL Cache

The TTL cache automatically expires entries after a specified time period.

```python
from cache import AsyncTTL

@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_weather(city: str) -> dict:
    # External API call
    weather = await weather_api.get_data(city)
    return weather
```

## Advanced Usage

### Working with Custom Objects

The cache works seamlessly with custom objects and ORM models:

```python
from dataclasses import dataclass
from cache import AsyncLRU

@dataclass
class UserFilter:
    age: int
    country: str
    status: str

@AsyncLRU(maxsize=128)
async def filter_users(filter_params: UserFilter) -> list:
    # Complex filtering operation
    users = await db.filter_users(
        age=filter_params.age,
        country=filter_params.country,
        status=filter_params.status
    )
    return users
```

### Skipping Arguments

Useful for methods where certain arguments shouldn't affect the cache key:

```python
from cache import AsyncTTL

class UserService:
    @AsyncTTL(time_to_live=300, maxsize=1000, skip_args=1)
    async def get_user_preferences(self, user_id: int) -> dict:
        # 'self' is skipped in cache key generation
        return await self.db.get_preferences(user_id)
```

### Cache Management

#### Bypassing Cache

```python
# Normal cached call
result = await get_user_data(123)

# Force fresh data
fresh_result = await get_user_data(123, use_cache=False)
```

#### Clearing Cache

```python
# Clear the entire cache
get_user_data.cache_clear()
```

## Performance Considerations

- The LRU cache is ideal for frequently accessed data with no expiration requirements
- The TTL cache is perfect for data that becomes stale after a certain period
- Choose `maxsize` based on your memory constraints and data access patterns
- Consider using `skip_args` when caching class methods to avoid instance-specific caching

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
