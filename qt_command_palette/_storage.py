from __future__ import annotations
from typing import Any, Callable, TypeVar
import inspect

_R = TypeVar("_R")


class Storage:
    """The variable storage."""

    _INSTANCES: dict[str, Storage] = {}

    def __init__(self):
        self._varmap: dict[str, Callable[[], Any]] = {}

    def mark_getter(self, name: str, func: Callable[[], Any] | None = None):
        def wrapper(f: Callable[[], Any]):
            self._varmap[name] = f
            return f

        return wrapper if func is None else wrapper(func)

    def mark_constant(self, name: str, value: Any):
        self._varmap[name] = lambda: value

    @classmethod
    def instance(cls, name: str = "") -> Storage:
        if name not in cls._INSTANCES:
            cls._INSTANCES[name] = Storage()
        return cls._INSTANCES[name]

    def call(self, func: Callable[..., _R]) -> _R:
        """Call a function with variables from the storage."""
        args = []
        for v in inspect.signature(func).parameters.keys():
            if getter := self._varmap.get(v, None):
                args.append(getter())
            else:
                raise ValueError(f"Variable {v} not found in storage")
        return func(*args)


def get_storage(name: str = "") -> Storage:
    """Get the name specific storage instance."""
    return Storage.instance(name)
