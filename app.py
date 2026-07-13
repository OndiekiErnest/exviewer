"""QApplication instance."""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

STYLE = """
QWidget {
    font-family: Consolas;
    font-size: 18px;
    letter-spacing: 0.1px;
}
"""

mainloop = QApplication(sys.argv)
mainloop.setStyle("Fusion")
mainloop.setStyleSheet(STYLE)

# check system theme
if styleh := mainloop.styleHints():
    IS_DARK = styleh.colorScheme() == Qt.ColorScheme.Dark
else:
    IS_DARK = False
