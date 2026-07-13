"""Custom QCalendar classes."""

from PyQt6.QtWidgets import QCalendarWidget


class CalendarWidget(QCalendarWidget):
    """Base calendar widget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
