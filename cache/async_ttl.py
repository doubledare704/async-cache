import time
from functools import wraps
from typing import Dict, Optional, Tuple, Coroutine
from asyncio import Lock
from copy import deepcopy

from .lru import LRU
from .types import T, AsyncFunc, Callable, Any


class TTL(LRU):
    """Time-To-Live (TTL) cache implementation extending LRU cache."""

    def __init__(self, maxsize: Optional[int] = 128, time_to_live: int = 0) -> None:
        super().__init__(maxsize=maxsize)
        self.time_to_live: int = time_to_live
        self.timestamps: Dict[Any, float] = {}

    async def contains(self, key: Any) -> bool:
        async with self._lock:
            if not key in self.cache:
                self._misses += 1
                return False
            
            if self.time_to_live:
                timestamp: float = self.timestamps.get(key, 0)
                if time.time() - timestamp > self.time_to_live:
                    del self.cache[key]
                    del self.timestamps[key]
                    self._misses += 1
                    return False
            
            self._hits += 1
            self.cache.move_to_end(key)
            return True

    async def get(self, key: Any) -> Any:
        async with self._lock:
            if self.time_to_live:
                timestamp: float = self.timestamps.get(key, 0)
                if time.time() - timestamp > self.time_to_live:
                    del self.cache[key]
                    del self.timestamps[key]
                    raise KeyError(key)
            self.cache.move_to_end(key)
            return deepcopy(self.cache[key])

    async def set(self, key: Any, value: Any) -> None:
        async with self._lock:
            if key in self.cache:
                self.cache.pop(key)
            elif self.maxsize and len(self.cache) >= self.maxsize:
                oldest_key, _ = self.cache.popitem(last=False)
                if self.time_to_live:
                    self.timestamps.pop(oldest_key, None)
            
            self.cache[key] = deepcopy(value)
            if self.time_to_live:
                self.timestamps[key] = time.time()

    async def clear(self) -> None:
        async with self._lock:
            self.cache.clear()
            self.timestamps.clear()
            self._hits = 0
            self._misses = 0


class AsyncTTL:
    """Async Time-To-Live (TTL) cache decorator."""

    def __init__(self, maxsize: Optional[int] = 128, time_to_live: int = 0, skip_args: int = 0) -> None:
        self.ttl = TTL(maxsize=maxsize, time_to_live=time_to_live)
        self.skip_args = skip_args

    def __call__(self, func: AsyncFunc) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, use_cache: bool = True, **kwargs: Any) -> T:
            if not use_cache:
                return await func(*args, **kwargs)

            key: Tuple[Any, ...] = (*args[self.skip_args:], *sorted(kwargs.items()))

            try:
                if await self.ttl.contains(key):
                    return await self.ttl.get(key)
            except KeyError:
                pass

            result: T = await func(*args, **kwargs)
            await self.ttl.set(key, result)
            return result

        async def cache_clear() -> None:
            await self.ttl.clear()

        wrapper.cache_clear = cache_clear  # type: ignore
        return wrapper
