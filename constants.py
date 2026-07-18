"""App constant values."""

import os
from datetime import datetime

APP_NAME = "exviewer"
APP_VERSION = "0.2.1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "appdata")

ICONS_DIR = os.path.join(DATA_DIR, "icons")

# created on demand and cleaned up on exit
# use a timestamp to avoid collisions between concurrent app instances
TEMP_DIR = os.path.join(DATA_DIR, datetime.now().strftime("%Y%m%d_%H%M%S_%f"))

APP_ICON = os.path.join(ICONS_DIR, "app.png")


# icon names
FILE_ICON = "mdi6.file-document-plus-outline"
INDEXALL_ICON = "fa6s.angles-down"
BOTTOM_ICON = "fa6s.angle-down"
SEARCH_ICON = "fa5s.search"
CALENDAR_ICON = "mdi6.calendar-search"
SPINNER_ICON = "fa6s.spinner"
COPY_ICON = "fa6s.copy"
