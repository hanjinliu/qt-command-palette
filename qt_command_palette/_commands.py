from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar
from typing_extensions import ParamSpec


_P = ParamSpec("_P")
_R = TypeVar("_R")

@dataclass
class Command(Generic[_P, _R]):
    function: Callable[_P, _R]
    title: str
    name: str
    tooltip: str = ""
    
    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        return self.function(*args, **kwargs)
    
    def fmt(self) -> str:
        return f"{self.title}: {self.name}"