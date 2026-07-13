"""App constant values."""

import os

APP_NAME = "ExViewer"
APP_VERSION = "0.1.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "appdata")

ICONS_DIR = os.path.join(DATA_DIR, "icons")

APP_ICON = os.path.join(ICONS_DIR, "app.png")


# icon names
FILE_ICON = "mdi6.file-document-plus-outline"
INDEXALL_ICON = "fa6s.angles-down"
BOTTOM_ICON = "fa6s.angle-down"
SEARCH_ICON = "fa5s.search"
CALENDAR_ICON = "mdi6.calendar-search"
SPINNER_ICON = "fa6s.spinner"
COPY_ICON = "fa6s.copy"
