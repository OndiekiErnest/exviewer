"""Custom QGroupBox widgets."""

from PyQt6.QtCore import QDate, QModelIndex, Qt
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout

from app import mainloop
from constants import CALENDAR_ICON, COPY_ICON, FILE_ICON, INDEXALL_ICON, SPINNER_ICON
from models.messages import MessagesModel

from .buttons import Button
from .frames import SearchFrame
from .labels import SelectableLabel
from .lineedits import LineEdit, PwdEdit
from .listviews import ListView
from .menus import CalendarMenu
from .utils import qicon
from .widgets import AnimatedIconWidget


class ChatBox(QGroupBox):
    """A QGroupBox that displays chat messages and its functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.search_results: list[QModelIndex] | None = None
        self.search_index = -1  # current search index

        tlayout = QHBoxLayout()
        tlayout.setContentsMargins(0, 0, 0, 0)

        blayout = QHBoxLayout()
        blayout.setAlignment(Qt.AlignmentFlag.AlignRight)
        blayout.setContentsMargins(0, 0, 0, 0)

        mlayout = QVBoxLayout(self)
        mlayout.addLayout(tlayout)

        self.calendar_menu = CalendarMenu()
        self.calendar_menu.cal.clicked.connect(self._scroll_to_date)

        self.file_btn = Button()
        self.file_btn.setToolTip("Open WhatsApp export")
        self.file_btn.setIcon(qicon(FILE_ICON))

        self.indexall_btn = Button()
        self.indexall_btn.setToolTip("Scroll to the bottom")
        self.indexall_btn.setIcon(qicon(INDEXALL_ICON))
        self.indexall_btn.clicked.connect(self._on_indexall)

        self.copy_btn = Button()
        self.copy_btn.setToolTip("Copy selected messages")
        self.copy_btn.setIcon(qicon(COPY_ICON))
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self.copy_messages)

        self.sending = LineEdit()
        self.sending.setPlaceholderText("Sender's name")

        self.zip_pwd = PwdEdit()
        self.zip_pwd.setPlaceholderText("ZIP Password")
        self.zip_pwd.hide()

        self.calendar_btn = Button()
        self.calendar_btn.setToolTip("Scroll to date")
        self.calendar_btn.setIcon(qicon(CALENDAR_ICON))
        self.calendar_btn.setMenu(self.calendar_menu)

        self.search_area = SearchFrame()
        self.search_area.search_edit.textChanged.connect(self._on_search)
        self.search_area.prev_btn.clicked.connect(self.go_prev)
        self.search_area.next_btn.clicked.connect(self.go_next)

        self.status_label = SelectableLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.messages_view = ListView()

        self.spinner = AnimatedIconWidget(SPINNER_ICON)
        self.spinner.hide()

        tlayout.addWidget(self.file_btn)
        tlayout.addSpacing(10)
        tlayout.addWidget(self.indexall_btn)
        tlayout.addWidget(self.copy_btn)
        tlayout.addSpacing(10)
        tlayout.addWidget(self.sending)
        # tlayout.addSpacing(10)
        tlayout.addWidget(self.zip_pwd)
        tlayout.addStretch()
        tlayout.addWidget(self.calendar_btn)
        tlayout.addWidget(self.search_area)

        mlayout.addWidget(self.messages_view)

        blayout.addWidget(self.status_label)
        blayout.addWidget(self.spinner)

        mlayout.addLayout(blayout)

    def set_messages(self, messages: MessagesModel):
        """set the messages model to the view"""
        self.messages_view.set_messages(messages)

        messages.signals.started.connect(self._insert_started)
        messages.signals.finished.connect(self._insert_finished)
        messages.signals.errored.connect(self._insert_errored)

        if selection_model := self.messages_view.selectionModel():
            selection_model.selectionChanged.connect(self._on_selection)

    def model(self):
        """get the messages model or none"""
        return self.messages_view.get_model()

    def go_next(self):
        """go to the next search result"""
        if not self.search_results:
            return

        next_index = (self.search_index + 1) % len(self.search_results)
        self._search_result_at(next_index)

    def go_prev(self):
        """go to the previous search result"""
        if not self.search_results:
            return

        prev_index = (self.search_index - 1) % len(self.search_results)
        self._search_result_at(prev_index)

    def copy_messages(self):
        """copy the messages in the search results to the clipboard"""
        selected = self.messages_view.selectedIndexes()
        if not selected:
            return

        if model := self.model():
            messages = model.as_text(selected)

            if clipboard := mainloop.clipboard():
                clipboard.setText(messages)

                self.copy_btn.setEnabled(False)

    def sendername(self):
        """return the sender's name"""
        return self.sending.text().strip()

    def set_sendername(self, name: str):
        """set the sender's name"""
        self.sending.setText(name)

    def set_pwd(self, pwd: str):
        """set the ZIP password and toggle visibility based on whether it's empty"""
        self.zip_pwd.setText(pwd)

    def pwd(self):
        """return the encoded ZIP password if visible, otherwise None"""
        if self.zip_pwd.isVisible():
            return self.zip_pwd.text().encode()

    def toggle_pwd(self, show: bool):
        """toggle the ZIP password input visibility"""
        self.zip_pwd.setVisible(show)

    def _on_selection(self, *args):
        """toggle copy button based on selection"""
        selected = self.messages_view.selectedIndexes()
        self.copy_btn.setEnabled(bool(selected))

    def _search_result_at(self, index: int):
        """scroll to search result by index"""
        if not self.search_results:
            return

        self.search_index = index
        mindex = self.search_results[index]

        self.messages_view.scroll_to_index(mindex)

        self.search_area.set_index(index + 1, len(self.search_results))

    def _insert_started(self, batch_size: int | str):
        """slot for when insert starts"""
        self.spinner.show()
        msg = (
            f"Reading the next {batch_size:,} messages..."
            if isinstance(batch_size, int)
            else f"Reading {batch_size} messages..."
        )
        self.status_label.setText(msg)

    def _insert_finished(self, total_messages: int):
        """slot for when insert finishes"""
        self.spinner.hide()
        # display total messages loaded (comma-separated)
        self.status_label.setText(f"Loaded messages: {total_messages:,}")

    def _insert_errored(self, error: Exception):
        """slot for when insert errors"""
        self.spinner.hide()
        self.status_label.setText(f"Error while reading messages: {error}")

    def _on_indexall(self):
        """slot for calling an index-all"""

        if model := self.model():
            if model.reader.ended():
                self.messages_view.scroll_to_bottom()
                return

            model.signals.finished.connect(self._after_indexall)
            model.indexer.index_all()

    def _after_indexall(self, _):
        """slot to scroll to the bottom after an index-all, and disconnect from the signal"""

        self.messages_view.scroll_to_bottom()
        if model := self.model():
            model.signals.finished.disconnect(self._after_indexall)

    def _on_search(self, query: str):
        """perform a search"""
        if not query:
            self.search_area.toggle_nav(False)
            return

        if model := self.model():
            self.search_index = -1

            self.search_results = model.search(query)

            self.search_area.toggle_nav(bool(self.search_results))

            self.go_next()

    def _scroll_to_date(self, date: QDate):
        """scroll to the first message with date"""
        if model := self.model():
            if indexes := model.search_date(date.toString("yyyyMMdd")):
                self.messages_view.scroll_to_index(indexes[0])
