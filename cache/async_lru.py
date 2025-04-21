from collections.abc import Coroutine
from functools import wraps
from typing import Any, Callable, Optional

from .lru import LRU
from .stats import CacheInfo
from .types import AsyncFunc


class AsyncLRU:
    """Async Least Recently Used (LRU) cache decorator."""

    def __init__(self, maxsize: Optional[int] = 128, skip_args: int = 0) -> None:
        """
        Initialize AsyncLRU cache.

        Args:
            maxsize: Maximum size of the cache. If None, cache size is unlimited.
            skip_args: Number of initial positional arguments to skip in the cache key.
                      Useful for methods where 'self' or 'cls' should not affect caching.
        """
        self.lru: LRU = LRU(maxsize=maxsize)
        self.skip_args: int = skip_args

    def __call__(self, func: AsyncFunc) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, use_cache: bool = True, **kwargs: Any) -> Any:
            if not use_cache:
                return await func(*args, **kwargs)

            key = (*args[self.skip_args:], *sorted(kwargs.items()))

            if await self.lru.contains(key):
                return await self.lru.get(key)

            result = await func(*args, **kwargs)
            await self.lru.set(key, result)
            return result

        async def cache_clear() -> None:
            await self.lru.clear()

        async def cache_info() -> CacheInfo:
            return await self.lru.get_stats()

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_info = cache_info  # type: ignore[attr-defined]
        return wrapper
