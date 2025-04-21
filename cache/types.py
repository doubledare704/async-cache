from collections.abc import Coroutine
from typing import Any, Callable, Dict, Tuple, TypeVar, Union

T = TypeVar("T")  # Generic return type
CacheKey = Union[Tuple[Any, ...], str]
AsyncFunc = Callable[..., Coroutine[Any, Any, T]]
CacheDict = Dict[Any, Any]
