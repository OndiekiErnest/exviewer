"""Custom QDialog widgets."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout

from .labels import SelectableLabel
from .lineedits import LineEdit


class SenderNameDialog(QDialog):
    """Dialog for entering the sender name."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Sender's name")
        self.setMinimumWidth(400)
        self.setMaximumWidth(500)
        self.setModal(True)

        # layout
        mlayout = QVBoxLayout(self)
        mlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mlayout.setSpacing(20)

        self.name_edit = LineEdit()
        self.name_edit.setPlaceholderText("Sender's name")

        self.continue_btn = QPushButton("Continue")
        self.continue_btn.setDefault(True)
        self.continue_btn.clicked.connect(self.accept)

        tlabel = SelectableLabel(
            "Enter the WhatsApp name of the sender\n(as it appears in the file)"
        )
        tlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        mlayout.addWidget(tlabel)

        mlayout.addWidget(self.name_edit)
        mlayout.addWidget(self.continue_btn)
