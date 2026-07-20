"""Custom PyQt6 QListView classes."""

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtWidgets import QAbstractItemView, QListView

from models.messages import MessagesModel

from .delegates import MessageBubbleDelegate


class ListView(QListView):
    """Custom QListView class with a chat-style appearance."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the scroll mode to ScrollPerPixel to slow down scrolling
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        if vscroll := self.verticalScrollBar():
            vscroll.setSingleStep(20)

        # hide scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # enable extended selection mode (ctrl+click to select multiple items)
        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

        # resize every time the list view is resized
        self.setResizeMode(QListView.ResizeMode.Adjust)

        # set item delegate to custom MessageBubbleDelegate
        self.setItemDelegate(MessageBubbleDelegate())

    def get_model(self):
        """return messages model or none"""
        if model := self.model():
            if isinstance(model, MessagesModel):
                return model

    def set_messages(self, messages: MessagesModel):
        """
        set the messages model as the source model,
        close the previous messages model if it exists
        """
        if model := self.get_model():
            model.close()

        self.setModel(messages)

    def scroll_to_index(self, index: QModelIndex):
        """scroll to index"""
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self.setCurrentIndex(index)

    def scroll_to_bottom(self):
        """scroll to the bottom of the list view"""
        if model := self.get_model():
            index = model.index(model.rowCount() - 1, 0)
            self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtBottom)
