from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar


_R = TypeVar("_R")


@dataclass
class Command(Generic[_R]):
    """A command representation."""

    function: Callable[..., _R]
    title: str
    desc: str
    tooltip: str = ""

    def __call__(self) -> _R:
        return self.function()

    def fmt(self) -> str:
        """Format command for display in the palette."""
        if self.title:
            return f"{self.title}: {self.desc}"
        return self.desc

    def matches(self, input_text: str) -> bool:
        """Return True if the command matches the input text."""
        fmt = self.fmt().lower()
        words = input_text.lower().split(" ")
        return all(word in fmt for word in words)
