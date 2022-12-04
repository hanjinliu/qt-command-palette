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

    @property
    def commands(self) -> list[Command]:
        return self._commands.copy()

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
        """
        Register a function to the command palette.
        """
        if len(args) > 0 and callable(args[0]):
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

    def show_widget(self, parent: Any = __default) -> None:
        """Show command palette widget."""
        self.get_widget(parent).show()
        return None

    def install(self, parent: QtW.QWidget, keys: str | None = None) -> None:
        """
        Install command palette on a Qt widget.

        Parameters
        ----------
        parent : QtW.QWidget
            The widget to install on.
        keys : str, optional
            If given, this key sequence will be used to show the command palette.
        """
        widget = self.get_widget(parent)
        widget.install_to(parent)
        if keys is not None:
            _register_shortcut(keys, parent, lambda: self.show_widget(parent))
        return None


class CommandGroup:
    def __init__(self, title: str, parent: CommandPalette) -> None:
        self._palette_ref = weakref.ref(parent)
        self._title = title

    def __repr__(self) -> str:
        return f"CommandGroup<{self.title}>"

    @property
    def palette(self) -> CommandPalette:
        """The parent command palette object."""
        if palette := self._palette_ref():
            return palette
        raise RuntimeError("CommandPalette is already destroyed.")

    @property
    def title(self) -> str:
        """The title of this group."""
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
        if len(args) > 0:
            args = args[:1] + (self.title,) + args[1:]
        else:
            args = (self.title,)

        return self.palette.register(*args, **kwargs)


def _register_shortcut(keys: str, parent: QtW.QWidget, target: Callable):
    """Register a callback to a key-binding globally."""
    from qtpy import QT6, QtGui

    if QT6:
        from qtpy.QtGui import QShortcut
    else:
        from qtpy.QtWidgets import QShortcut

    shortcut = QShortcut(QtGui.QKeySequence(keys), parent)
    shortcut.activated.connect(target)
    return None


_GLOBAL_PALETTES: dict[str, CommandPalette] = {}
_DEFAULT_PALETTE = CommandPalette()


def get_palette(name: str | None = None) -> CommandPalette:
    """
    Get the global command palette object.

    Examples
    --------
    >>> palette = get_palette()  # get the default palette
    >>> palette = get_palette("my_module")  # get a palette for specific app
    """
    global _GLOBAL_PALETTES

    if name is None:
        return _DEFAULT_PALETTE
    if not isinstance(name, str):
        raise TypeError(f"Expected str, got {type(name).__name__}")
    if (palette := _GLOBAL_PALETTES.get(name, None)) is None:
        palette = _GLOBAL_PALETTES[name] = CommandPalette()
    return palette


def add_group(title: str) -> CommandGroup:
    """
    Add a command group to the global command palette.

    Examples
    --------
    >>> group = add_group("My Commands")
    """
    return get_palette().add_group(title)


@overload
def register(
    func: _F,
    title: str | None,
    desc: str | None = None,
    tooltip: str | None = None,
) -> _F:
    ...


@overload
def register(
    title: str | None,
    desc: str | None = None,
    tooltip: str | None = None,
) -> Callable[[_F], _F]:
    ...


def register(*args, **kwargs):
    """
    Register a function to the global command palette.

    Examples
    --------
    >>> @register
    ... def my_command():
    ...     print("Hello World!")
    >>> @register("My Command")
    ... def my_command():
    ...     print("Hello World!")
    """
    return get_palette().register(*args, **kwargs)
