"""Text file reader based on mmap."""

import logging
import mmap
from datetime import datetime
from pathlib import Path

from .datastructs import Offset

logger = logging.getLogger(__name__)


class Reader:
    """A text file reader that uses mmap for efficient random-access reading."""

    # faster attribute access and memory optimization
    __slots__ = ("mapped_file", "filename")

    def __init__(self, filename: Path | None = None):
        # variables
        self.mapped_file: mmap.mmap | None = None
        self.filename: Path | None = None

        if filename:
            self.open_txt(filename)

    def open_txt(self, filename: Path):
        """opens the file for reading using mmap"""

        # close any existing file
        self.close()

        self.filename = filename

        with filename.open("rb") as f:
            self.mapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

            logger.debug(f"opened file: {filename!r}")

    def read(self, offset: Offset):
        """reads from the file using the given offset"""
        if self.mapped_file is None:
            return

        try:
            return self.mapped_file[offset.start : offset.end].decode(
                errors="surrogateescape"
            )

        except IndexError as ie:  # out of bounds
            logger.exception(ie)
            return

        except ValueError as ve:  # invalid range
            logger.exception(ve)
            return

    def readline(self) -> str:
        """reads a single line from the file"""
        if self.mapped_file is None:
            return ""

        line = self.mapped_file.readline()
        return line.decode(errors="surrogateescape")

    def tell(self) -> int:
        """returns the current position in the file"""
        if self.mapped_file is None:
            return 0

        return self.mapped_file.tell()

    def seek(self, offset: int):
        """seeks to the given position in the file"""
        if self.mapped_file is None:
            return

        self.mapped_file.seek(offset)

    def filesize(self) -> int:
        """returns the size of the file in bytes"""
        if self.mapped_file is None:
            return 0

        return self.mapped_file.size()

    def modified_at(self):
        """returns a datetime object representing the last modified time of the file"""
        if self.filename is None:
            return None

        return datetime.fromtimestamp(self.filename.stat().st_mtime)

    def ended(self) -> bool:
        """returns whether the file has ended"""
        if self.mapped_file is None:
            return True

        return self.mapped_file.tell() == self.mapped_file.size()

    def close(self):
        """closes the file"""
        if self.mapped_file is not None:
            self.mapped_file.close()

            self.mapped_file = None
            self.filename = None

            logger.debug("closed mmap file")

    def __del__(self):
        """destructor - closes the file"""
        self.close()
