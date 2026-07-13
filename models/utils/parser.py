"""Message parser."""

import re
from datetime import datetime
from typing import Iterable

from .datastructs import Message, Offset
from .reader import Reader


class MessageParser:
    """Message parser that uses regex to parse messages from a Reader."""

    # faster attribute access and memory optimization
    __slots__ = ("reader", "sender")

    # matches the first line of a WhatsApp message.
    # e.g. 01/01/23, 12:00 PM - Sender name: Message content
    MESSAGE_PATTERN = re.compile(
        r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}), "
        r"(?P<time>\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s*-\s*"
        r"(?P<content>.+)$"
    )

    # supported timestamp formats.
    DATETIME_FORMATS = (
        "%m/%d/%y, %I:%M %p",  # e.g. 01/01/23, 12:00 PM
        "%m/%d/%Y, %I:%M %p",  # e.g. 01/01/2023, 12:00 PM
        "%d/%m/%y, %H:%M",  # e.g. 01/01/23, 15:00
        "%d/%m/%Y, %H:%M",  # e.g. 01/01/2023, 15:00
    )

    def __init__(self, reader: Reader, sender: str):
        # variables
        self.reader = reader
        self.sender = sender

    @classmethod
    def is_message_start(cls, line: str) -> bool:
        """check if the line is the start of a new message"""
        return cls.MESSAGE_PATTERN.match(line) is not None

    @classmethod
    def parse_datetime(
        cls,
        date: str,
        time: str,
    ) -> datetime:
        """parse a timestamp based on the supported formats"""
        value = f"{date}, {time}"

        for fmt in cls.DATETIME_FORMATS:
            try:
                return datetime.strptime(value, fmt)

            except ValueError:
                pass

        # raise so we can fix it
        raise ValueError(f"Unsupported timestamp format: {value}")

    def next_message(self) -> Message | None:
        """build a Message matching a regex pattern from the current position in the reader"""
        offset_start = self.reader.tell()

        first_line = self.reader.readline()
        if not first_line:
            return

        # use tuple to consume the generator, so offset_end works as expected
        subsequent_lines = tuple(self._subsequent_lines())
        offset_end = self.reader.tell()

        offset = Offset(start=offset_start, end=offset_end)
        return self._create_message(first_line, subsequent_lines, offset)

    def message_at(self, offset: Offset) -> Message | None:
        """return the message at the given offset"""
        message_text = self.reader.read(offset)
        if message_text is None:
            return

        # create message
        lines = message_text.splitlines()

        if not lines:
            return

        return self._create_message(lines[0], lines[1:], offset)

    def get_offset(self, start_at: int | None = None):
        """return the offset of the next message starting at the given position"""
        if start_at is not None:
            self.reader.seek(start_at)

        offset_start = self.reader.tell()

        # pop first line
        first_line = self.reader.readline()
        if not first_line:
            return

        # ensure first line is a message start
        if not self.is_message_start(first_line):
            return

        offset_end = self.reader.tell()

        while line := self.reader.readline():
            if self.is_message_start(line):
                # unprocessed line, seek back so we start from there next we call readline()
                self.reader.seek(offset_end)
                break

            offset_end = self.reader.tell()

        return Offset(start=offset_start, end=offset_end)

    def _subsequent_lines(self):
        """read all the lines that make a full message, until we hit the start of the next message"""

        offset_end = self.reader.tell()

        while line := self.reader.readline():
            if self.is_message_start(line):
                # unprocessed line, seek back so we start from there next we call readline()
                self.reader.seek(offset_end)
                break

            offset_end = self.reader.tell()

            yield line

    def _create_message(
        self,
        first_line: str,
        subsequent_lines: Iterable[str],
        offset: Offset,
    ) -> Message | None:
        """create a Message from the given first line and subsequent lines"""
        match = self.MESSAGE_PATTERN.match(first_line)
        if match is None:
            return

        sent_at = self.parse_datetime(
            match.group("date"),
            match.group("time"),
        )
        content = match.group("content")

        sender = ""
        text = content

        # handle normal user message
        if ": " in content:
            sender, text = content.split(": ", 1)
        # else, it's a system message

        other_lines = "\n".join(subsequent_lines)

        # use str.join to handle cases where the lines are empty ('\n' isn't added in that case)
        full_text = "\n".join((text, other_lines))

        return Message(
            sender=sender,
            sent=(self.sender == sender),
            sent_at=sent_at,
            text=full_text,
            offset=offset,
        )
