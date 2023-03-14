from __future__ import annotations

from qtpy import QtWidgets as QtW, QtGui, QtCore
from qtpy.QtCore import Qt, Signal

from ._list import QCommandList
from ._commands import Command


class QCommandLineEdit(QtW.QLineEdit):
    """The line edit used in command palette widget."""

    def commandPalette(self) -> QCommandPalette:
        """The parent command palette widget."""
        return self.parent()

    def event(self, e: QtCore.QEvent):
        if e.type() != QtCore.QEvent.Type.KeyPress:
            return super().event(e)
        e = QtGui.QKeyEvent(e)
        if e.modifiers() in (
            Qt.KeyboardModifier.NoModifier,
            Qt.KeyboardModifier.KeypadModifier,
        ):
            key = e.key()
            if key == Qt.Key.Key_Escape:
                self.commandPalette().hide()
                return True
            elif key == Qt.Key.Key_Return:
                palette = self.commandPalette()
                if palette._list.can_execute():
                    self.commandPalette().hide()
                    self.commandPalette()._list.execute()
                    return True
                else:
                    return False
            elif key == Qt.Key.Key_Up:
                self.commandPalette()._list.move_selection(-1)
                return True
            elif key == Qt.Key.Key_Down:
                self.commandPalette()._list.move_selection(1)
                return True
        return super().event(e)


class QCommandPalette(QtW.QWidget):
    """A Qt command palette widget."""

    hidden = Signal()

    def __init__(self, parent: QtW.QWidget = None):
        super().__init__(parent)

        self._line = QCommandLineEdit()
        self._list = QCommandList()
        _layout = QtW.QVBoxLayout(self)
        _layout.addWidget(self._line)
        _layout.addWidget(self._list)
        self.setLayout(_layout)

        self._line.textChanged.connect(self._on_text_changed)
        self._list.commandClicked.connect(self._on_command_clicked)
        self._line.editingFinished.connect(self.hide)

    def match_color(self) -> str:
        """The color used for the matched characters."""
        return self._list.matchColor

    def set_match_color(self, color):
        """Set the color used for the matched characters."""
        self._list.matchColor = QtGui.QColor(color)

    def add_command(self, cmd: Command):
        self._list.add_command(cmd)
        return None

    def extend_command(self, list_of_commands: list[Command]):
        self._list.extend_command(list_of_commands)
        return None

    def clear_commands(self):
        self._list.clear_commands()
        return None

    def install_to(self, parent: QtW.QWidget):
        self.setParent(parent, Qt.WindowType.SubWindow)
        self.hide()

    def _on_text_changed(self, text: str):
        self._list.update_for_text(text)
        return None

    def _on_command_clicked(self, index: int):
        self._list.execute(index)
        self.hide()
        return None

    def focusOutEvent(self, a0: QtGui.QFocusEvent) -> None:
        self.hide()
        return super().focusOutEvent(a0)

    def show(self):
        self._line.setText("")
        self._list.update_for_text("")
        super().show()
        if parent := self.parentWidget():
            parent_rect = parent.rect()
            self_size = self.size()
            w = min(int(parent_rect.width() * 0.8), self_size.width())
            topleft = parent.rect().topLeft()
            topleft.setX(int(topleft.x() + (parent_rect.width() - w) / 2))
            topleft.setY(int(topleft.y() + 3))
            self.move(topleft)
            self.resize(w, self_size.height())

        self.raise_()
        self._line.setFocus()
        return None

    def show_center(self):
        """Show command palette widget in the center of the screen."""
        self._line.setText("")
        self._list.update_for_text("")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        super().show()

        screen_rect = QtGui.QGuiApplication.primaryScreen().geometry()
        self.resize(screen_rect.width() * 0.5, screen_rect.height() * 0.5)
        point = screen_rect.center() - self.rect().center()
        self.move(point)

        self.raise_()
        self._line.setFocus()
        return None

    def hide(self):
        self.hidden.emit()
        return super().hide()
