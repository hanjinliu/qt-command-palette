from __future__ import annotations

from enum import Enum
from functools import wraps
from typing import Any, Callable, TypeVar, overload, TYPE_CHECKING
import weakref
import inspect
from ._commands import Command
from ._storage import Storage

if TYPE_CHECKING:
    from ._widget import QCommandPalette
    from qtpy import QtWidgets as QtW

    WVDict = weakref.WeakValueDictionary[int, Any]

_F = TypeVar("_F", bound=Callable)


def _always_true() -> bool:
    return True


@inspect.signature
def register_with_func(
    func: Callable,
    title: str | None = None,
    desc: str | None = None,
    tooltip: str | None = None,
    when: Callable[[], bool] = _always_true,
):
    """Template function to provide signature to register() with 'func' argument."""


@inspect.signature
def register_without_func(
    title: str | None = None,
    desc: str | None = None,
    tooltip: str | None = None,
    when: Callable[[], bool] = _always_true,
):
    """Template function to provide signature to register() without 'func' argument."""


class Alignment(Enum):
    """Alignment flag of the palette."""

    parent = "parent"  # align to the parent widget
    screen = "screen"  # align to the screen


class CommandPalette:
    """The command palette interface."""

    def __init__(
        self, name: str, *, alignment: str | Alignment = Alignment.parent
    ) -> None:
        self._commands: list[Command] = []
        self._parent_to_palette_map: dict[int, QCommandPalette] = {}
        self._palette_to_parent_map: WVDict = weakref.WeakValueDictionary()
        self._name = name
        self._alignment = Alignment(alignment)

    @property
    def alignment(self) -> Alignment:
        """Alignment flag of the palette."""
        return self._alignment

    @property
    def commands(self) -> list[Command]:
        """List of all the commands."""
        return self._commands.copy()

    @overload
    def register(
        self,
        func: _F,
        title: str | None,
        desc: str | None = None,
        tooltip: str | None = None,
        when: Callable[[], bool] = _always_true,
    ) -> _F:
        ...

    @overload
    def register(
        self,
        title: str | None,
        desc: str | None = None,
        tooltip: str | None = None,
        when: Callable[[], bool] = _always_true,
    ) -> Callable[[_F], _F]:
        ...

    def register(self, *args, **kwargs):
        """Register a function to the command palette."""
        if len(args) > 0 and callable(args[0]):
            bound = register_with_func.bind(*args, **kwargs)
        else:
            bound = register_without_func.bind(*args, **kwargs)

        bound.apply_defaults()
        bound_args = bound.arguments
        func = bound_args.pop("func", None)

        # update defaults
        title: str | None = bound_args["title"]
        desc: str | None = bound_args["desc"]
        tooltip: str | None = bound_args["tooltip"]
        when: Callable[..., bool] = bound_args["when"]

        if title is None:
            title = ""

        def wrapper(func: _F) -> _F:
            nonlocal title, desc, tooltip
            if desc is None:
                desc = getattr(func, "__name__", repr(func))
            if tooltip is None:
                tooltip = getattr(func, "__doc__", "") or ""

            storage = Storage.instance(self._name)

            @wraps(func)
            def _func(qpallete):
                parent = self._palette_to_parent_map[id(qpallete)]
                return storage.call(func, parent)

            cmd = Command(_func, title, desc, tooltip, when)
            self._commands.append(cmd)
            return func

        return wrapper if func is None else wrapper(func)

    def add_group(self, title: str) -> CommandGroup:
        """Add a group to the command palette."""
        return CommandGroup(title, parent=self)

    __default = object()

    def get_widget(self, parent: Any = __default) -> QCommandPalette:
        """Get a command palette widget for the given parent widget."""
        from ._widget import QCommandPalette

        _id = id(parent)
        if (widget := self._parent_to_palette_map.get(_id)) is None:
            widget = QCommandPalette()
            widget.extend_command(self._commands)
            self._parent_to_palette_map[_id] = widget
            self._palette_to_parent_map[id(widget)] = parent
        return widget

    def show_widget(self, parent: Any = __default) -> None:
        """Show command palette widget."""
        if self.alignment is Alignment.parent:
            self.get_widget(parent).show()
        else:
            self.get_widget(parent).show_center()
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

    def update(self, parent: QtW.QWidget | None = None):
        """Update command palette install to the given parent widget."""
        if parent is None:
            for p in self._palette_to_parent_map.values():
                self.update(p)
            return None
        _id = id(parent)
        widget = self._parent_to_palette_map[_id]
        widget.clear_commands()
        widget.extend_command(self._commands)
        return None

    def sort(
        self, rule: Callable[[Command], Any] | None = None, reverse: bool = False
    ) -> None:
        """Sort the command palette."""
        if rule is None:

            def rule(cmd):
                return cmd.title + cmd.desc

        self._commands.sort(key=rule, reverse=reverse)
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
        self,
        func: _F,
        desc: str | None = None,
        tooltip: str | None = None,
        when: Callable[[], bool] = _always_true,
    ) -> _F:
        ...

    @overload
    def register(
        self,
        desc: str | None = None,
        tooltip: str | None = None,
        when: Callable[[], bool] = _always_true,
    ) -> Callable[[_F], _F]:
        ...

    def register(self, *args, **kwargs):
        if "title" in kwargs:
            raise TypeError("register() got an unexpected keyword argument 'title'")
        if len(args) > 0:
            if callable(args[0]):
                args = args[:1] + (self.title,) + args[1:]
            else:
                args = (self.title,) + args
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
_DEFAULT_PALETTE = CommandPalette(name="default")


def get_palette(
    name: str | None = None,
    *,
    alignment: str | Alignment = Alignment.parent,
) -> CommandPalette:
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
        palette = _GLOBAL_PALETTES[name] = CommandPalette(
            name=name, alignment=alignment
        )
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
    when: Callable[[], bool] = _always_true,
) -> _F:
    ...


@overload
def register(
    title: str | None,
    desc: str | None = None,
    tooltip: str | None = None,
    when: Callable[[], bool] = _always_true,
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
