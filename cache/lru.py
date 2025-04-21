from asyncio import Lock
from collections import OrderedDict
from typing import Any, Optional


class LRU:
    """Thread-safe LRU cache implementation."""

    def __init__(self, maxsize: Optional[int] = 128) -> None:
        self.maxsize: Optional[int] = maxsize
        self.cache: OrderedDict = OrderedDict()
        self._lock: Lock = Lock()

    async def contains(self, key: Any) -> bool:
        return key in self.cache

    async def get(self, key: Any) -> Any:
        value: Any = self.cache.pop(key)
        self.cache[key] = value
        return value

    async def set(self, key: Any, value: Any) -> None:
        if key in self.cache:
            self.cache.pop(key)
        elif self.maxsize and len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        self.cache[key] = value

    async def clear(self) -> None:
        self.cache.clear()
