from __future__ import annotations
from typing import Any, Callable, TypeVar

_R = TypeVar("_R")


class Storage:
    """The variable storage."""

    _INSTANCES: dict[str, Storage] = {}

    def __init__(self):
        self._varmap: dict[str, Callable[[], Any]] = {}

    def mark_getter(self, name: str):
        def wrapper(f: Callable[[], Any]):
            self._varmap[name] = f
            return f

        return wrapper

    def mark_constant(self, name: str, value: Any):
        self._varmap[name] = lambda: value

    @classmethod
    def instance(cls, name: str = "") -> Storage:
        if name not in cls._INSTANCES:
            cls._INSTANCES[name] = Storage()
        return cls._INSTANCES[name]

    def call(self, func: Callable[..., _R]) -> _R:
        varnames = func.__code__.co_varnames
        args = []
        for v in varnames:
            if getter := self._varmap.get(v, None):
                args.append(getter())
            else:
                raise ValueError(f"Variable {v} not found in storage")
        return func(*args)


def get_storage(name: str = "") -> Storage:
    return Storage.instance(name)
