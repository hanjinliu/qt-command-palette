from __future__ import annotations
from typing import Any, TYPE_CHECKING
import logging

from qtpy import QtWidgets as QtW, QtGui, QtCore
from qtpy.QtCore import Qt, Signal

from ._commands import Command

logger = logging.getLogger(__name__)

class QCommandMatchModel(QtCore.QAbstractListModel):
    def __init__(self, parent: QtW.QWidget = None):
        super().__init__(parent)
        self._commands: list[Command] = []
    
    def rowCount(self, parent: QtCore.QModelIndex = None) -> int:
        return min(len(self._commands), 12)
    
    def columnCount(self, parent: QtCore.QModelIndex = None) -> int:
        return 1
    
    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.ToolTipRole:
            if not index.isValid():
                return QtCore.QVariant()
            cmd = self._commands[index.row()]
            return cmd.tooltip
        return QtCore.QVariant()
    
    def flags(self, index: QtCore.QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class QCommandLabel(QtW.QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self._command_text = text
    
    def command_text(self) -> str:
        return self._command_text

    def set_match(self, input_text: str, /):
        text = self.command_text()
        colored_text = f"<b><font color='blue'>{input_text}</font></b>"
        text_new = text.replace(input_text, colored_text)
        self.setText(text_new)
        return None
    
    def set_highlight(self, highlight: bool):
        if highlight:
            self.setStyleSheet("border: 4px solid blue;")
        else:
            self.setStyleSheet("border: none;")
  

class QCommandList(QtW.QListView):
    clicked = Signal(int)  # one of the items is clicked
    
    def __init__(self, parent: QtW.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModel(QCommandMatchModel(self))
        self.setSelectionMode(QtW.QAbstractItemView.SelectionMode.NoSelection)
        self._selected_index = 0
    
    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        index = self.indexAt(e.pos())
        if index.isValid():
            self.clicked(index.row())
            return None
    
    def move_highlight(self, dx: int) -> None:
        self._selected_index += dx
        self._selected_index = max(0, self._selected_index)
        self._selected_index = min(len(self.model()._commands) - 1, self._selected_index)
        self.update_highlight()
        return None
    
    def update_highlight(self):
        for i in range(self.model().rowCount()):
            label = self.indexWidget(self.model().index(i))
            label.set_highlight(i == self._selected_index)
        return None
        
    def add_command(self, command: Command) -> None:
        self.model()._commands.append(command)
        self.setIndexWidget(
            self.model().index(len(self.model()._commands) - 1), 
            QCommandLabel(command.fmt())
        )
    
    def execute(self):
        cmd = self.model()._commands[self._selected_index]
        logger.debug(f"executing command: {cmd.fmt()}")
        cmd()
        
    def update_for_text(self, input_text: str) -> None:
        self._selected_index = 0
        for idx, cmd in enumerate(self.model()._commands):
            show = input_text in cmd.fmt()
            self.setRowHidden(idx, not show)
            if show:
                label = self.indexWidget(self.model().index(idx))
                label.set_match(input_text)
        self.update_highlight()
        self.update()
        return None

    if TYPE_CHECKING:
        def model(self) -> QCommandMatchModel: ...
        def indexWidget(self, index: QtCore.QModelIndex) -> QCommandLabel: ...