"""Custom QLineEdit classes."""

from PyQt6.QtWidgets import QLineEdit

from .utils import qicon


class LineEdit(QLineEdit):
    """Base line edit"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SearchLineEdit(QLineEdit):
    """Custom search box widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setClearButtonEnabled(True)
        self.setPlaceholderText("Search...")

        self.addAction(qicon("fa5s.search"), QLineEdit.ActionPosition.LeadingPosition)
