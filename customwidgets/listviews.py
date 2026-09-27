"""Custom PyQt6 QListView classes."""

import logging

from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QContextMenuEvent
from PyQt6.QtWidgets import QAbstractItemView, QListView, QMessageBox, QMenu

from models.messages import MessagesModel
from models.recentfiles import FilesListModel

from .delegates import MessageBubbleDelegate

logger = logging.getLogger(__name__)


class MessagesListView(QListView):
    """Custom QListView class with a chat-style appearance."""

    row_changed = pyqtSignal(int)  # emit the current row when it changes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the scroll mode to ScrollPerPixel to slow down scrolling
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        if vscroll := self.verticalScrollBar():
            vscroll.valueChanged.connect(self.on_vscroll)
            vscroll.setSingleStep(20)

        # hide scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # enable extended selection mode (ctrl+click to select multiple items)
        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

        # adjust every time the list view is resized
        self.setResizeMode(QListView.ResizeMode.Adjust)

        # set item delegate to custom MessageBubbleDelegate
        self.setItemDelegate(MessageBubbleDelegate())

    def get_model(self):
        """return messages model or none"""
        if model := self.model():
            if isinstance(model, MessagesModel):
                return model

            else:
                print("Model is not a MessagesModel")

        else:
            print("Model is None")

    def set_messages(self, messages: MessagesModel):
        """
        set the messages model as the list view model,
        close the previous messages model if it exists
        """

        print("Setting messages model")
        if model := self.get_model():
            model.close()

        self.setModel(messages)

    def on_vscroll(self, _):
        """get the top visible row when the list view is scrolled"""

        index = self.indexAt(QPoint(1, 1))

        if index.isValid():
            top_row = index.row()
            self.row_changed.emit(top_row)

    def scroll_to_index(self, index: QModelIndex):
        """scroll to index"""
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self.setCurrentIndex(index)
        print(f"Scrolled to index: {index.row()}")

    def scroll_to_row(self, row: int):
        """scroll to row"""
        if model := self.get_model():
            print(f"Scrolling to row: {row}, model row count: {model.rowCount()}")
            if 0 <= row < model.rowCount():
                index = model.index(row, 0)
                self.scroll_to_index(index)

    def scroll_to_bottom(self):
        """scroll to the bottom of the list view"""
        if model := self.get_model():
            index = model.index(model.rowCount() - 1, 0)
            self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtBottom)


class RecentFilesListView(QListView):
    """Custom QListView for recent files."""

    # emit a sorted list of selected rows
    selection_changed = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.setTextElideMode(Qt.TextElideMode.ElideMiddle)

    def _confirm(self, message: str):
        """ask a user to confirm deletion/clear"""
        reply = QMessageBox.question(self, "Confirm Action", message)
        return reply == QMessageBox.StandardButton.Yes

    def setModel(self, model: FilesListModel):
        """set the model for the list view"""
        # disconnect selection signal in old selection model
        if old_selection_model := self.selectionModel():
            old_selection_model.selectionChanged.disconnect(self.on_selection_changed)
            logger.debug(
                "disconnected selectionChanged signal from old selection model"
            )

        super().setModel(model)

        if selection_model := self.selectionModel():
            selection_model.selectionChanged.connect(self.on_selection_changed)
            logger.debug("connected selectionChanged signal to a selection model")

    def on_selection_changed(self):
        """handle selection changes"""
        selected = sorted(
            (index.row() for index in self.selectedIndexes()),
            reverse=True,
        )
        self.selection_changed.emit(selected)

    def delete_selected(self):
        """delete selected items from the list view"""
        if model := self.model():
            if isinstance(model, FilesListModel):
                if self._confirm("Are you sure you want to delete the selected files?"):
                    indexes = {index.row() for index in self.selectedIndexes()}
                    model.removeRandom(indexes)

    def clear(self):
        """clear the list view"""
        if model := self.model():
            if isinstance(model, FilesListModel):
                if self._confirm("Are you sure you want to clear the list?"):
                    model.clear_files()
                    logger.debug("cleared files from model")

    def contextMenuEvent(self, a0: QContextMenuEvent | None):
        # create a menu with delete and clear actions

        if a0 is None:
            return

        model = self.model()

        if model is None:
            logger.debug("model is None, cannot show context menu")
            return

        if not isinstance(model, FilesListModel):
            logger.debug("model is not a FilesListModel, cannot show context menu")
            return

        menu = QMenu(self)

        delete_action = menu.addAction("Delete")
        if delete_action is not None:
            delete_action.setEnabled(bool(self.selectedIndexes()))

        clear_action = menu.addAction("Clear")
        if clear_action is not None:
            clear_action.setEnabled(bool(model))

        action = menu.exec(a0.globalPos())

        if action == delete_action:
            self.delete_selected()

        elif action == clear_action:
            self.clear()
