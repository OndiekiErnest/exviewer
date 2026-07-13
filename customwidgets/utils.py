"""Widget utility functions."""

from PyQt6.QtWidgets import QWidget
from qtawesome import Pulse, icon


def qicon(name: str, *args, **kwargs):
    """return a styled qtawesome icon"""
    return icon(name, *args, **kwargs)


def qpulsing_animation(parent: QWidget, **kwargs):
    """return a styled qtawesome Pulse animation"""
    return Pulse(parent, **kwargs)
