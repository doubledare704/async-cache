import time
from functools import wraps
from typing import Dict, Optional, Tuple, Coroutine
from asyncio import Lock

from .lru import LRU
from .types import T, AsyncFunc, Callable, Any


class TTL(LRU):
    """Time-To-Live (TTL) cache implementation extending LRU cache."""

    def __init__(self, maxsize: Optional[int] = 128, time_to_live: int = 0) -> None:
        super().__init__(maxsize=maxsize)
        self.time_to_live: int = time_to_live
        self.timestamps: Dict[Any, float] = {}
        self._lock = Lock()

    async def contains(self, key: Any) -> bool:
        async with self._lock:
            exists = await super().contains(key)
            if not exists:
                return False
            if self.time_to_live:
                timestamp: float = self.timestamps.get(key, 0)
                if time.time() - timestamp > self.time_to_live:
                    del self.cache[key]
                    del self.timestamps[key]
                    return False
            return True

    async def get(self, key: Any) -> Any:
        async with self._lock:
            return await super().get(key)

    async def set(self, key: Any, value: Any) -> None:
        async with self._lock:
            await super().set(key, value)
            if self.time_to_live:
                self.timestamps[key] = time.time()

    async def clear(self) -> None:
        async with self._lock:
            await super().clear()
            self.timestamps.clear()


class AsyncTTL:
    """Async Time-To-Live (TTL) cache decorator."""

    def __init__(self,
                 time_to_live: int = 0,
                 maxsize: Optional[int] = 128,
                 skip_args: int = 0) -> None:
        self.ttl: TTL = TTL(maxsize=maxsize, time_to_live=time_to_live)
        self.skip_args: int = skip_args

    def __call__(self, func: AsyncFunc) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, use_cache: bool = True, **kwargs: Any) -> T:
            if not use_cache:
                return await func(*args, **kwargs)

            key: Tuple[Any, ...] = (*args[self.skip_args:], *sorted(kwargs.items()))

            if await self.ttl.contains(key):
                try:
                    return await self.ttl.get(key)
                except Exception:
                    pass

            result: T = await func(*args, **kwargs)
            try:
                await self.ttl.set(key, result)
            except Exception:
                pass
            return result

        wrapper.cache_clear = self.ttl.clear  # type: ignore
        return wrapper
