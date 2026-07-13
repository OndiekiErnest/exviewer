"""
Application entry point.
"""

if __name__ == "__main__":
    import sys

    from app import mainloop
    from gui import MainWindow

    args = sys.argv

    window = MainWindow()
    window.showMaximized()

    if len(args) > 1:
        passed_file = args[1]

        window.open_chat_file(filename=passed_file)

    sys.exit(mainloop.exec())
