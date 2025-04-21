from typing import NamedTuple, Optional


class CacheInfo(NamedTuple):
    """Statistics for cache performance."""
    hits: int
    misses: int
    maxsize: Optional[int]
    currsize: int