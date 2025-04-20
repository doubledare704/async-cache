from typing import Any, Dict, Tuple

from .types import CacheKey


class KEY:
    """
    A hashable key class for cache implementations that handles complex arguments.
    Supports primitive types, tuples, dictionaries, and objects with __dict__.
    """

    def __init__(self, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
        self.args: Tuple[Any, ...] = args
        self.kwargs: Dict[str, Any] = {k: v for k, v in kwargs.items() if k != "use_cache"}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KEY):
            return NotImplemented
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        def _hash(param: Any) -> CacheKey:
            if isinstance(param, tuple):
                return tuple(_hash(item) for item in param)
            if isinstance(param, dict):
                return tuple(sorted((_hash(k), _hash(v)) for k, v in param.items()))
            elif hasattr(param, "__dict__"):
                return str(sorted(vars(param).items()))
            return str(param)

        return hash(_hash(self.args) + _hash(self.kwargs))
