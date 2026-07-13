"""Custom QFrame classes."""

from PyQt6.QtWidgets import QFrame, QHBoxLayout

from .buttons import Button
from .labels import SelectableLabel
from .lineedits import SearchLineEdit
from .utils import qicon


class SearchFrame(QFrame):
    """Search results navigation widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(600)

        mlayout = QHBoxLayout(self)
        mlayout.setContentsMargins(0, 0, 0, 0)

        self.index_label = SelectableLabel()

        self.search_edit = SearchLineEdit()

        self.prev_btn = Button()
        self.prev_btn.setIcon(qicon("fa6s.chevron-left"))

        self.next_btn = Button()
        self.next_btn.setIcon(qicon("fa6s.chevron-right"))

        mlayout.addWidget(self.search_edit, stretch=3)
        mlayout.addWidget(self.prev_btn, stretch=0)
        mlayout.addWidget(self.next_btn, stretch=0)
        mlayout.addWidget(self.index_label, stretch=1)

        self.toggle_nav(False)

    def toggle_nav(self, enable: bool):
        """enable/disable navigation"""
        self.prev_btn.setEnabled(enable)
        self.next_btn.setEnabled(enable)
        # if buttons are disabled, clear to avoid confusion
        if not enable:
            self.index_label.clear()

    def has_prev(self, has: bool):
        """toggle the prev btn"""
        self.prev_btn.setEnabled(has)

    def has_next(self, has: bool):
        """toggle the next btn"""
        self.next_btn.setEnabled(has)

    def set_index(self, index: int, total: int):
        """set the current results index"""
        self.index_label.setText(f"{index:,} of {total:,}")
