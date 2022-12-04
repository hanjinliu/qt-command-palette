from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar


_R = TypeVar("_R")


@dataclass
class Command(Generic[_R]):
    function: Callable[[], _R]
    title: str
    name: str
    tooltip: str = ""

    def __call__(self) -> _R:
        return self.function()

    def fmt(self) -> str:
        """Format command for display in the palette."""
        return f"{self.title}: {self.name}"

    def matches(self, input_text: str) -> bool:
        """Return True if the command matches the input text."""
        return input_text in self.fmt()
