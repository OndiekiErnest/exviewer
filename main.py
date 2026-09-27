"""
Application entry point.
"""

from utils import remove_temp_dir
from models.recentfiles import recent_files_model

def cleanup():
    """cleanup before exiting"""

    recent_files_model.save_to_file()
    remove_temp_dir()


if __name__ == "__main__":
    import sys

    from app import mainloop
    from gui import MainWindow

    mainloop.aboutToQuit.connect(cleanup)

    args = sys.argv

    window = MainWindow()
    window.showMaximized()

    if len(args) > 1:
        passed_file = args[1]

        window.open_chat_file(filename=passed_file)

    sys.exit(mainloop.exec())
