"""Messages data model."""

from pathlib import Path

from PyQt6.QtCore import QAbstractListModel, QModelIndex, QObject, Qt, pyqtSignal

from .utils.cache import MessageCache
from .utils.datastructs import Message
from .utils.indexer import OffsetIndexer
from .utils.parser import MessageParser
from .utils.reader import Reader


class ModelSignals(QObject):
    """Signals for the messages model."""

    started = pyqtSignal(object)
    """insert started signal, emits the batch size or 'all'"""

    finished = pyqtSignal(int)
    """insert finished signal"""

    errored = pyqtSignal(str)
    """insert errored signal"""


class MessagesModel(QAbstractListModel):
    """Data model for the messages list."""

    # faster attribute access and memory optimization
    __slots__ = ("signals", "reader", "parser", "indexer", "messages_cache")

    BATCH_SIZE = 50

    def __init__(
        self,
        filename: Path,
        sender: str,
        *args,
        cache: MessageCache | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.signals = ModelSignals()

        self.reader = Reader(filename=filename)

        self.parser = MessageParser(self.reader, sender)

        self.indexer = OffsetIndexer(self.parser)
        self.indexer.signals.errored.connect(self.signals.errored)
        self.indexer.signals.started.connect(self.signals.started)
        self.indexer.signals.finished.connect(self._insert_finished)
        self.indexer.signals.index_changed.connect(self._model_updated)

        self.messages_cache = cache or MessageCache(100)

    def __str__(self) -> str:
        return f"Messages model of {self.rowCount()} rows"

    def rowCount(self, parent=None) -> int:
        """return the number of rows in the model"""
        return len(self.indexer)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """return the data for the given index and role"""
        if not index.isValid():
            return None

        row = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            # handle the display role
            return self._display_role(row)

        elif role == Qt.ItemDataRole.UserRole:
            return self._search_role(row)

        elif role == Qt.ItemDataRole.UserRole + 1:
            return self._date_role(row)

    def canFetchMore(self, parent: QModelIndex) -> bool:
        """return whether more data can be fetched for the given index"""
        return not self.reader.ended()

    def fetchMore(self, parent: QModelIndex):
        """fetch more data for the given index"""
        if not self.canFetchMore(parent):
            return

        # index more offsets
        self.indexer.index_batch(self.BATCH_SIZE)

    def search(self, query: str, start: int = 0, count: int = -1):
        """search for messages matching the given query"""
        return self.match(
            self.index(start, 0),
            Qt.ItemDataRole.UserRole,
            query,
            hits=count,
            flags=Qt.MatchFlag.MatchContains,
        )

    def search_date(self, query_date: str, start: int = 0):
        """return the first index of message matching the query date"""
        return self.match(
            self.index(start, 0),
            Qt.ItemDataRole.UserRole + 1,
            query_date,  # date in the format YYYYMMDD
            hits=1,  # return only 1 result
            flags=Qt.MatchFlag.MatchExactly,
        )

    def as_text(self, indexes: list[QModelIndex]):
        """return the messages in order of their index as a string"""
        # sort indexes by their row
        indexes.sort(key=lambda index: index.row())
        # create a single string with the messages separated by newlines
        text = "\n".join(
            (
                str(message)
                for index in indexes
                if isinstance(
                    (message := self.data(index, Qt.ItemDataRole.DisplayRole)), Message
                )
            )
        )
        return text

    def close(self):
        """release resources used by the model"""
        self.reader.close()
        self.indexer.clear()
        self.messages_cache.clear()

    def _display_role(self, index: int):
        """handle the display role for the given index"""
        # check if the message is already cached
        if index in self.messages_cache:
            # faster access
            return self.messages_cache[index]

        offset = self.indexer[index]
        message = self.parser.message_at(offset)

        if message:
            # cache the message for faster access later
            self.messages_cache[index] = message
            # return it
            return message

    def _search_role(self, index: int):
        """handle the filter role"""
        if message := self._display_role(index):
            return message.text

    def _date_role(self, index: int):
        """handle the filter by date string role"""
        if message := self._display_role(index):
            return message.sent_at.strftime("%Y%m%d")

    def _model_updated(self):
        """slot to handle the indexer updated signal"""
        # indexer updated for some reason, reset the model
        self.beginResetModel()
        self.endResetModel()
        self.signals.finished.emit(len(self.indexer))

    def _insert_finished(self, indexed: int):
        """slot to handle the finished signal from the indexer"""

        index_len = len(self.indexer)
        # since the indexer has already added the new offsets, we subtract indexed to get start
        start = index_len - indexed
        last = index_len - 1

        if indexed:  # guard against 0 rows indexed
            self.beginInsertRows(QModelIndex(), start, last)
            self.endInsertRows()

        self.signals.finished.emit(index_len)
