"""Custom QDialog widgets."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout

from .labels import SelectableLabel
from .lineedits import LineEdit, PwdEdit


class EditDialog(QDialog):
    """Dialog for getting a one-line text."""

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

        self.edit = LineEdit()
        self.edit.setPlaceholderText("Sender's name")
        self.edit.textChanged.connect(self._on_text_changed)

        self.pwd = PwdEdit()
        self.pwd.setPlaceholderText("ZIP password")
        self.pwd.textChanged.connect(self._on_text_changed)
        self.pwd.hide()

        self.ok_btn = QPushButton("Continue")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)

        tlabel = SelectableLabel(
            "Enter the WhatsApp name of the sender\n(as it appears in the file)"
        )
        tlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        mlayout.addWidget(tlabel)

        mlayout.addWidget(self.edit)
        mlayout.addWidget(self.pwd)
        mlayout.addWidget(self.ok_btn)

    def _on_text_changed(self, _: str):
        text = self.name()
        enable = (
            bool(text) and bool(self.pwd.text()) if self.pwd.isVisible() else bool(text)
        )
        self.ok_btn.setEnabled(enable)

    def toggle_password(self, show: bool):
        """show or hide the password field"""
        self.pwd.setVisible(show)

    def name(self):
        """return the text entered by the user"""
        return self.edit.text().strip()

    def password(self):
        """return the pwd entered by the user"""
        # don't strip password because a pwd can end with a space
        return self.pwd.text()

    def set_name(self, text: str):
        """set the text in the edit field"""
        self.edit.setText(text)

    def set_password(self, text: str):
        """set the password in the field"""
        self.pwd.setText(text)
