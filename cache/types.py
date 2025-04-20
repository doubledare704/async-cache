from typing import TypeVar, Callable, Coroutine, Any, Dict, Tuple, Union

T = TypeVar('T')  # Generic return type
CacheKey = Union[Tuple[Any, ...], str]
AsyncFunc = Callable[..., Coroutine[Any, Any, T]]
CacheDict = Dict[Any, Any]