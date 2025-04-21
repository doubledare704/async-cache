from asyncio import Lock
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Optional

from .stats import CacheInfo


class LRU:
    """Thread-safe LRU cache implementation with statistics tracking."""

    def __init__(self, maxsize: Optional[int] = 128) -> None:
        self.maxsize: Optional[int] = maxsize
        self.cache: OrderedDict = OrderedDict()
        self._hits: int = 0
        self._misses: int = 0
        self._lock = Lock()

    async def contains(self, key: Any) -> bool:
        async with self._lock:
            exists = key in self.cache
            if exists:
                self._hits += 1
                # Move to end to maintain LRU order
                self.cache.move_to_end(key)
            else:
                self._misses += 1
            return exists

    async def get(self, key: Any) -> Any:
        async with self._lock:
            # Move to end and return copy
            self.cache.move_to_end(key)
            return deepcopy(self.cache[key])

    async def set(self, key: Any, value: Any) -> None:
        async with self._lock:
            if key in self.cache:
                self.cache.pop(key)
            elif self.maxsize and len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)
            self.cache[key] = deepcopy(value)

    async def clear(self) -> None:
        async with self._lock:
            self.cache.clear()
            self._hits = 0
            self._misses = 0

    async def get_stats(self) -> CacheInfo:
        """Get current cache statistics."""
        async with self._lock:
            return CacheInfo(
                hits=self._hits,
                misses=self._misses,
                maxsize=self.maxsize,
                currsize=len(self.cache)
            )
