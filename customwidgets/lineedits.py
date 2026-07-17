"""Custom QLineEdit classes."""

from PyQt6.QtGui import QAction
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


class PwdEdit(QLineEdit):
    """custom QLineEdit for masked display, with show/hide"""

    __slots__ = ("show_action",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.show_action = QAction(self)
        self.addAction(self.show_action, QLineEdit.ActionPosition.TrailingPosition)

        self.show_action.triggered.connect(self.set_hide)
        self.set_hide()

    def set_show(self):
        """show contents"""
        self.show_action.triggered.disconnect(self.set_show)
        self.show_action.setToolTip("Hide")
        self.show_action.setIcon(qicon("fa6.eye-slash"))
        self.setEchoMode(QLineEdit.EchoMode.Normal)
        # when clicked again, hide
        self.show_action.triggered.connect(self.set_hide)

    def set_hide(self):
        """hide contents"""
        self.show_action.triggered.disconnect(self.set_hide)
        self.show_action.setToolTip("Show")
        self.show_action.setIcon(qicon("fa6.eye"))
        # set masked input
        self.setEchoMode(QLineEdit.EchoMode.Password)
        # when clicked again, show
        self.show_action.triggered.connect(self.set_show)
