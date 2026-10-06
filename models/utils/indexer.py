"""Indexer for the model."""

from PyQt6.QtCore import QObject, QThreadPool, pyqtSignal

from .datastructs import Offset
from .parser import MessageParser
from .runnables import IndexingWorker


class IndexerSignals(QObject):
    """Defines the signals available from the indexer."""

    started = pyqtSignal(object)
    """emitted with the batch size or 'all' when indexing starts"""

    finished = pyqtSignal(int)
    """emitted with the number of offsets indexed when indexing finishes"""

    index_changed = pyqtSignal()
    """emitted when the indexer is cleared"""

    errored = pyqtSignal(str)
    """emitted when indexing errors"""

    resume_ready = pyqtSignal(int)
    """emitted when indexer has loaded enough rows to resume, emits resume_row"""


class OffsetIndexer(QObject):
    """
    A list of offsets that can be used to navigate through a file.

    Offsets can be accessed by index, and the indexer can be cleared.

    Example:
        >>> indexer = OffsetIndexer(parser)
        >>> offset_1 = indexer[0]
    """

    # faster attribute access and memory optimization
    __slots__ = ("parser", "offsets", "signals", "thread_pool")

    def __init__(
        self, parser: MessageParser, *args, resume_row: int | None = None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.parser = parser
        self.offsets: list[Offset] = []

        self.signals = IndexerSignals()

        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

        if resume_row:
            # index right away
            self.index_at_least(resume_row)

    def __len__(self) -> int:
        return len(self.offsets)

    def __getitem__(self, index: int) -> Offset:
        return self.offsets[index]

    def index_at_least(self, rows):
        """index enough rows to resume/scroll to"""

        def on_worker_finished(loaded: int):
            """slot for the finished signal"""
            self.signals.finished.emit(loaded)
            self.signals.resume_ready.emit(rows)

        batch = 50
        already_loaded = len(self.offsets)
        to_load = max(rows - already_loaded, batch)
        # make to_load a multiple of BATCH
        to_load = ((to_load + batch - 1) // batch) * batch

        worker = IndexingWorker(self.parser, self.offsets, to_load)
        # forward the signals from the worker to the indexer
        worker.signals.started.connect(self.signals.started)
        worker.signals.errored.connect(self.signals.errored)
        worker.signals.finished.connect(on_worker_finished)

        self.thread_pool.start(worker)

    def index_batch(self, batch_size: int = 50):
        """
        delegate indexing to a worker thread to avoid blocking the UI

        the offset list will be extended in the worker thread
        """

        worker = IndexingWorker(self.parser, self.offsets, batch_size)
        # forward the signals from the worker to the indexer
        worker.signals.started.connect(self.signals.started)
        worker.signals.errored.connect(self.signals.errored)
        worker.signals.finished.connect(self.signals.finished)

        self.thread_pool.start(worker)

    def index_all(self):
        """index all messages in the file"""
        self.index_batch(batch_size=-1)  # -1 means index all messages

    def to_list(self):
        """serialize offsets to a list"""
        return [offset.to_dict() for offset in self.offsets]

    def from_list(self, data: list):
        """deserialize offsets from a list"""
        self.offsets = [Offset.from_dict(offset_data) for offset_data in data]
        self.signals.index_changed.emit()

    def clear(self):
        """clear the offsets"""
        self.offsets.clear()

        self.signals.index_changed.emit()
