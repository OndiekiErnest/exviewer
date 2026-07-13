"""Custom QMenu classes."""

from PyQt6.QtWidgets import QMenu, QWidgetAction

from .calendars import CalendarWidget


class CalendarMenu(QMenu):
    """A menu that pops up a calendar widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cal = CalendarWidget()

        action = QWidgetAction(self)
        action.setDefaultWidget(self.cal)

        self.addAction(action)
