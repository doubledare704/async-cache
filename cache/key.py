from typing import Any, Dict, Tuple


class KEY:
    """
    A hashable key class for cache implementations that handles complex arguments.
    Supports primitive types, tuples, dictionaries, and objects with __dict__.
    """

    def __init__(self, args: "Tuple[Any, ...]", kwargs: "Dict[str, Any]") -> None:
        self.args: "Tuple[Any, ...]" = args
        self.kwargs: Dict[str, Any] = {
            k: v for k, v in kwargs.items() if k != "use_cache"
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KEY):
            return NotImplemented
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        # Fix operator issue by converting to string first
        return hash(str(self.args) + str(sorted(self.kwargs.items())))
