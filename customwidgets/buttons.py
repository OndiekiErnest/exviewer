"""Custom QPushButton classes."""

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QPushButton, QSizePolicy


class Button(QPushButton):
    """A custom QPushButton."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(24, 24))
        # disable expanding
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
