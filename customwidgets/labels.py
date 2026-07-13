"""Custom QLabel widgets."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy


class SelectableLabel(QLabel):
    """A QLabel that can be selected and copied."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextInteractionFlags(
            self.textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
