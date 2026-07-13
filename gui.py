"""
Main application window for the WhatsApp chat viewer.
"""

from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon

from constants import APP_NAME, APP_ICON
from customwidgets.dialogs import SenderNameDialog
from customwidgets.groupboxes import ChatBox
from models.messages import MessagesModel


class MainWindow(QWidget):
    """
    Main application window.

    Allows the user to:
        - Select a WhatsApp export (.txt)
        - Enter the sender's account name
        - View the chat
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setMinimumSize(1200, 600)

        mlayout = QVBoxLayout(self)
        mlayout.setContentsMargins(0, 0, 0, 0)

        self.file_path: Path | None = None
        self.last_known_dir = Path("~").expanduser() / "Documents"

        self.chat_viewer = ChatBox()
        self.chat_viewer.file_btn.clicked.connect(self.open_chat_file)

        self.chat_viewer.sending.returnPressed.connect(self._reload_chat)

        mlayout.addWidget(self.chat_viewer)

    def open_chat_file(self, filename: str | None = None):
        """open a file selection dialog and load the selected chat file"""

        if not filename:
            # select from dialog
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Open WhatsApp Export",
                str(self.last_known_dir),
                "Text Files (*.txt)",
            )

        if not filename:
            return

        self.file_path = Path(filename)
        self.last_known_dir = self.file_path.parent

        name_dialog = SenderNameDialog(self)
        name_dialog.name_edit.setText(self.chat_viewer.sending.text().strip())

        if name_dialog.exec():
            self.chat_viewer.sending.setText(name_dialog.name_edit.text())

        else:
            return

        self._reload_chat()

    def _reload_chat(self):
        """build the message index and display the chat"""

        if self.file_path is None:
            return

        sender = self.chat_viewer.sending.text().strip()

        if not sender:
            QMessageBox.warning(
                self,
                "Sender Required",
                "Please enter the sender's WhatsApp account name.",
            )
            return

        # create a new messages model with the selected file and sender
        model = MessagesModel(self.file_path, sender)
        # set the model to the chat viewer
        self.chat_viewer.set_messages(model)

    def closeEvent(self, event):
        """close the messages model when the window is closed"""
        if model := self.chat_viewer.model():
            if isinstance(model, MessagesModel):
                # close the model here because it is not time consuming,
                # and won't freeze the UI
                model.close()

        super().closeEvent(event)
