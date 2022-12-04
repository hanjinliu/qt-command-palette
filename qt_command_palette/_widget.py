from __future__ import annotations

from qtpy import QtWidgets as QtW, QtGui
from qtpy.QtCore import Qt

from ._list import QCommandList
from ._commands import Command


class QCommandPalette(QtW.QDialog):
    """
    A Qt command palette widget.
    """

    def __init__(self, parent: QtW.QWidget = None):
        super().__init__(parent)

        self._line = QtW.QLineEdit()
        self._list = QCommandList()
        _layout = QtW.QVBoxLayout(self)
        _layout.addWidget(self._line)
        _layout.addWidget(self._list)
        self.setLayout(_layout)

        self._line.textChanged.connect(self._on_text_changed)
        self._list.commandClicked.connect(self._on_command_clicked)

    def add_command(self, cmd: Command):
        self._list.add_command(cmd)
        return None

    def extend_command(self, list_of_commands: list[Command]):
        self._list.extend_command(list_of_commands)
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

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.modifiers() == Qt.KeyboardModifier.NoModifier:
            key = a0.key()
            if key == Qt.Key.Key_Escape:
                self.hide()
            elif key == Qt.Key.Key_Return:
                self._list.execute()
                self.hide()
            elif key == Qt.Key.Key_Up:
                self._list.move_highlight(-1)
            elif key == Qt.Key.Key_Down:
                self._list.move_highlight(1)
        return super().keyPressEvent(a0)

    def show(self):
        self._line.setText("")
        self._list.update_for_text("")
        super().show()
        if parent := self.parentWidget():
            parent_rect = parent.rect()
            self_size = self.size()
            w, _ = self_size.width(), self_size.height()
            topleft = parent.rect().topLeft()
            topleft.setX(topleft.x() + (parent_rect.width() - w) / 2)
            topleft.setY(topleft.y() + 3)
            self.move(topleft)

        self._line.setFocus()
        return None
