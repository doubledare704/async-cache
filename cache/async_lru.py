from functools import wraps
from typing import Optional, Coroutine

from .key import KEY
from .lru import LRU
from .types import T, AsyncFunc, Callable, Any


class AsyncLRU:
    """Async Least Recently Used (LRU) cache decorator."""

    def __init__(self, maxsize: Optional[int] = 128) -> None:
        self.lru: LRU = LRU(maxsize=maxsize)

    def __call__(self, func: AsyncFunc) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, use_cache: bool = True, **kwargs: Any) -> T:
            if not use_cache:
                return await func(*args, **kwargs)

            key: KEY = KEY(args, kwargs)

            if await self.lru.contains(key):
                return await self.lru.get(key)

            result: T = await func(*args, **kwargs)
            await self.lru.set(key, result)
            return result

        wrapper.cache_clear = self.lru.clear  # type: ignore
        return wrapper
