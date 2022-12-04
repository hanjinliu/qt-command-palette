from __future__ import annotations
from typing import Any, Callable, TypeVar, overload, TYPE_CHECKING
import weakref
import inspect
from ._commands import Command

if TYPE_CHECKING:
    from ._widget import QCommandPalette
    from qtpy import QtWidgets as QtW

_F = TypeVar("_F", bound=Callable)


@inspect.signature
def register_with_func(
    func: Callable,
    title: str | None = None,
    desc: str | None = None,
    tooltip: str | None = None,
):
    """Template function to provide signature to register() with 'func' argument."""


@inspect.signature
def register_without_func(
    title: str | None = None, desc: str | None = None, tooltip: str | None = None
):
    """Template function to provide signature to register() without 'func' argument."""


class CommandPalette:
    """The command palette interface."""

    def __init__(self) -> None:
        self._commands: list[Command] = []
        self._widget_map: dict[int, QCommandPalette] = {}

    @overload
    def register(
        self,
        func: _F,
        title: str | None,
        desc: str | None = None,
        tooltip: str | None = None,
    ) -> _F:
        ...

    @overload
    def register(
        self,
        title: str | None,
        desc: str | None = None,
        tooltip: str | None = None,
    ) -> Callable[[_F], _F]:
        ...

    def register(self, *args, **kwargs):
        if len(args) == 0:
            raise TypeError("register() requires at least 1 positional argument")
        if callable(args[0]):
            bound = register_with_func.bind(*args, **kwargs)
        else:
            bound = register_without_func.bind(*args, **kwargs)

        bound.apply_defaults()
        bound_args = bound.arguments
        func = bound_args.pop("func", None)

        # update defaults
        title = bound_args["title"]
        desc = bound_args["desc"]
        tooltip = bound_args["tooltip"]

        if title is None:
            title = ""
        if desc is None:
            desc = getattr(func, "__name__", repr(func))
        if tooltip is None:
            tooltip = getattr(func, "__doc__", "")

        def wrapper(func: _F) -> _F:
            cmd = Command(func, title, desc, tooltip)
            self._commands.append(cmd)
            return func

        return wrapper if func is None else wrapper(func)

    def add_group(self, title: str) -> CommandGroup:
        return CommandGroup(title, parent=self)

    __default = object()

    def get_widget(self, parent: Any = __default) -> QCommandPalette:
        from ._widget import QCommandPalette

        _id = id(parent)
        if (widget := self._widget_map.get(_id)) is None:
            widget = QCommandPalette()
            widget.extend_command(self._commands)
            self._widget_map[_id] = widget
        return widget

    def install(self, parent: QtW.QWidget, keys: str | None = None) -> None:
        widget = self.get_widget(parent)
        widget.install_to(parent)
        if keys is not None:
            register_shortcut(keys, parent, lambda: widget.show)
        return None


class CommandGroup:
    def __init__(self, title: str, parent: CommandPalette) -> None:
        self._palette_ref = weakref.ref(parent)
        self._title = title

    def __repr__(self) -> str:
        return f"CommandGroup<{self.title}>"

    @property
    def palette(self):
        if palette := self._palette_ref():
            return palette
        raise RuntimeError("CommandPalette is already destroyed.")

    @property
    def title(self) -> str:
        return self._title

    @overload
    def register(
        self, func: _F, desc: str | None = None, tooltip: str | None = None
    ) -> _F:
        ...

    @overload
    def register(
        self, desc: str | None = None, tooltip: str | None = None
    ) -> Callable[[_F], _F]:
        ...

    def register(self, *args, **kwargs):
        if "title" in kwargs:
            raise TypeError("register() got an unexpected keyword argument 'title'")
        kwargs["title"] = self.title
        return self.palette.register(*args, **kwargs)


def register_shortcut(keys: str, parent: QtW.QWidget, target: Callable):
    """Register a callback to a key-binding globally."""
    from qtpy import QT6, QtGui

    if QT6:
        from qtpy.QtGui import QShortcut
    else:
        from qtpy.QtWidgets import QShortcut

    shortcut = QShortcut(QtGui.QKeySequence(keys), parent)
    shortcut.activated.connect(target)
    return None


# global command palette

_COMMAND = CommandPalette()

register = _COMMAND.register
