"""Utilities that don't fit other files and are used throughout the included modules."""
from typing import Any, Tuple, Iterable


def loop_last(it: Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    """Enumerate like that returns true if on the last element instead of index."""
    iterable = iter(it)
    v = next(iterable)
    for val in iterable:
        yield False, v
        v = val
    yield True, v
