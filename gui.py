"""
Main application window for the WhatsApp chat viewer.
"""

from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QWidget

from constants import APP_ICON, APP_NAME
from customwidgets.dialogs import EditDialog
from customwidgets.groupboxes import ChatBox
from models.messages import MessagesModel
from utils import is_zip_encrypted


class MainWindow(QWidget):
    """
    Main application window.

    Allows the user to:
        - Select a WhatsApp export (.txt, .zip)
        - Enter the sender's account name
        - Enter the ZIP password, if the file is encrypted
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
        self.chat_viewer.zip_pwd.returnPressed.connect(self._reload_chat)

        mlayout.addWidget(self.chat_viewer)

    def open_chat_file(self, filename: str | None = None):
        """use the selected filename to create messages model"""

        if not filename:
            # select from dialog
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Open WhatsApp Export",
                str(self.last_known_dir),
                "Supported Files (*.txt *.zip)",
            )

        if not filename:
            return

        self.file_path = Path(filename)
        self.last_known_dir = self.file_path.parent

        # check if zip and if encrypted
        show_pwd = self.file_path.suffix == ".zip" and is_zip_encrypted(self.file_path)

        # always toggle the password visibility
        # whether the user closes the dialog or clicks 'continue'
        self.chat_viewer.toggle_pwd(show_pwd)

        name_dialog = EditDialog(self)
        name_dialog.set_name(self.chat_viewer.sendername())
        name_dialog.set_password(self.chat_viewer.zip_pwd.text())
        name_dialog.toggle_password(show_pwd)

        if name_dialog.exec():
            self.chat_viewer.set_pwd(name_dialog.password())
            self.chat_viewer.set_sendername(name_dialog.name())

        else:
            return

        self._reload_chat()

    def _reload_chat(self):
        """build the message model and display the chat"""

        if self.file_path is None:
            return

        sender = self.chat_viewer.sendername()

        if not sender:
            QMessageBox.warning(
                self,
                "Sender Required",
                "Please enter the sender's WhatsApp account name.",
            )
            return

        # None or bytes
        pwd = self.chat_viewer.pwd()

        try:
            # create a new messages model with the selected file and sender
            model = MessagesModel(self.file_path, sender, pwd)
            # set the model to the chat viewer
            self.chat_viewer.set_messages(model)

        except Exception as e:
            QMessageBox.critical(self, "Action Failed", str(e))

    def closeEvent(self, a0):
        """close the messages model when the window is closed"""
        if model := self.chat_viewer.model():
            if isinstance(model, MessagesModel):
                # close the model here because it is not time consuming,
                # and won't freeze the UI
                model.close()

        super().closeEvent(a0)
