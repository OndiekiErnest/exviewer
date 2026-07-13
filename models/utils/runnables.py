"""Custom PyQt6 QRunnable classes."""

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal

from .datastructs import Offset
from .parser import MessageParser


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    started = pyqtSignal(object)
    """offset indexing started signal, emits batch size or 'all'"""

    finished = pyqtSignal(int)
    """offset indexing finished signal, emits the number of offsets indexed"""

    errored = pyqtSignal(str)
    """offset indexing errored signal"""


class IndexingWorker(QRunnable):
    """Worker thread for indexing offsets in batches."""

    # faster attribute access and memory optimization
    __slots__ = ("parser", "offsets", "batch_size", "signals")

    def __init__(self, parser: MessageParser, offsets: list[Offset], batch_size: int):
        super().__init__()
        self.setAutoDelete(True)

        self.parser = parser
        self.offsets = offsets
        self.batch_size = batch_size
        self.signals = WorkerSignals()

    def run(self):
        """run the indexing logic in a separate thread"""
        try:
            # handle the case where self.batch_size is -1, index all available messages
            if self.batch_size == -1:
                self.signals.started.emit("all")

                new_offsets = self._all_offsets()

            else:
                self.signals.started.emit(self.batch_size)

                new_offsets = (
                    offset
                    for _ in range(self.batch_size)
                    if (offset := self.parser.get_offset())
                )

            # we can't call len(new_offsets) because it's a generator
            len_b4 = len(self.offsets)

            # update the offsets list
            self.offsets.extend(new_offsets)

            # the number offsets added may be less than the batch size
            self.signals.finished.emit(len(self.offsets) - len_b4)

        except Exception:
            self.signals.errored.emit("Something went wrong")

    def _all_offsets(self):
        """index the entire file, yield offsets"""

        while not self.parser.reader.ended():
            if offset := self.parser.get_offset():
                yield offset
