from __future__ import annotations
from typing import Any, TYPE_CHECKING, Iterator
import logging
import re

from qtpy import QtWidgets as QtW, QtCore
from qtpy.QtCore import Qt, Signal

from ._commands import Command

logger = logging.getLogger(__name__)


def colored(text: str, color: str) -> str:
    return f"<b><font color={color!r}>{text}</font></b>"


class QCommandMatchModel(QtCore.QAbstractListModel):
    """A list model for the command palette."""

    def __init__(self, parent: QtW.QWidget = None):
        super().__init__(parent)
        self._commands: list[Command] = []
        self._max_matches = 24

    def rowCount(self, parent: QtCore.QModelIndex = None) -> int:
        return self._max_matches

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        return QtCore.QVariant()

    def flags(self, index: QtCore.QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


class QCommandLabel(QtW.QLabel):
    """The label widget to display a command in the palette."""

    def __init__(self, cmd: Command | None = None):
        super().__init__()
        if cmd is not None:
            self.set_command(cmd)
        else:
            self._command_text = ""

    def command(self) -> Command:
        """Command bound to this label."""
        return self._command

    def set_command(self, cmd: Command) -> None:
        """Set command to this widget."""
        command_text = cmd.fmt()
        self._command_text = command_text
        self._command = cmd
        self.setText(command_text)
        self.setToolTip(cmd.tooltip)

    def command_text(self) -> str:
        """The original command text."""
        return self._command_text

    def set_text_colors(self, input_text: str, /, color: str = "blue"):
        """Set label text color based on the input text."""
        if input_text == "":
            return None
        text = self.command_text()
        words = input_text.split(" ")
        pattern = re.compile("|".join(words), re.IGNORECASE)

        output_texts: list[str] = []
        last_end = 0
        for match_obj in pattern.finditer(text):
            output_texts.append(text[last_end : match_obj.start()])
            word = match_obj.group()
            colored_word = colored(word, color)
            output_texts.append(colored_word)
            last_end = match_obj.end()
        output_texts.append(text[last_end:])

        self.setText("".join(output_texts))
        return None


class QCommandList(QtW.QListView):
    commandClicked = Signal(int)  # one of the items is clicked

    def __init__(self, parent: QtW.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModel(QCommandMatchModel(self))
        self.setSelectionMode(QtW.QAbstractItemView.SelectionMode.NoSelection)
        self._selected_index = 0
        self._label_widgets: list[QCommandLabel] = []
        self._current_max_index = 0
        for i in range(self.model()._max_matches):
            lw = QCommandLabel()
            self._label_widgets.append(lw)
            self.setIndexWidget(self.model().index(i), lw)
        self.pressed.connect(self._on_clicked)

        self._match_color = "#468cc6"

    def match_color(self) -> str:
        return self._match_color

    def set_match_color(self, color: str):
        self._match_color = color

    def _on_clicked(self, index: QtCore.QModelIndex) -> None:
        if index.isValid():
            self.commandClicked.emit(index.row())
            return None

    def move_selection(self, dx: int) -> None:
        self._selected_index += dx
        self._selected_index = max(0, self._selected_index)
        self._selected_index = min(self._current_max_index - 1, self._selected_index)
        self.update_selection()
        return None

    def update_selection(self):
        index = self.model().index(self._selected_index)
        self.selectionModel().setCurrentIndex(
            index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        return None

    @property
    def all_commands(self) -> list[Command]:
        return self.model()._commands

    def add_command(self, command: Command) -> None:
        self.all_commands.append(command)
        return None

    def extend_command(self, commands: list[Command]) -> None:
        """Extend the list of commands."""
        self.all_commands.extend(commands)
        return None

    def command_at(self, index: int) -> Command:
        return self.indexWidget(self.model().index(index)).command()

    def set_command_at(self, index: int, cmd: Command) -> None:
        self.indexWidget(self.model().index(index)).set_command(cmd)
        return None

    def iter_command(self) -> Iterator[Command]:
        for i in range(self.model().rowCount()):
            if not self.isRowHidden(i):
                yield self.command_at(i)

    def execute(self, index: int | None = None) -> None:
        """Execute the currently selected command."""
        if index is None:
            index = self._selected_index
        cmd = self.command_at(index)
        logger.debug(f"executing command: {cmd.fmt()}")
        cmd()
        # move to the top
        self.all_commands.remove(cmd)
        self.all_commands.insert(0, cmd)

    def update_for_text(self, input_text: str) -> None:
        """Update the list to match the input text."""
        self._selected_index = 0
        max_matches = self.model()._max_matches
        row = 0
        for cmd in self.all_commands:
            if cmd.matches(input_text):
                self.setRowHidden(row, False)
                lw = self.indexWidget(self.model().index(row))
                lw.set_command(cmd)
                lw.set_text_colors(input_text, color=self._match_color)
                row += 1

                if row >= max_matches:
                    self._current_max_index = max_matches
                    break
        else:
            self._current_max_index = row
            for row in range(row, max_matches):
                self.setRowHidden(row, True)
        self.update_selection()
        self.update()
        return None

    if TYPE_CHECKING:

        def model(self) -> QCommandMatchModel:
            ...

        def indexWidget(self, index: QtCore.QModelIndex) -> QCommandLabel:
            ...
