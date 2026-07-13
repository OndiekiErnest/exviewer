"""Data structures for the model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class Offset:
    """A file offset"""

    start: int
    end: int

    def __len__(self) -> int:
        """return the length of the offset"""
        return self.end - self.start

    def to_dict(self) -> dict[str, int]:
        """return the offset as a dictionary"""
        return {"start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, offset: dict[str, int]) -> "Offset":
        """create an offset from a dictionary"""
        return cls(start=offset["start"], end=offset["end"])


@dataclass(slots=True, kw_only=True)
class Message:
    """A message dataclass"""

    sender: str
    sent: bool
    sent_at: datetime
    text: str
    offset: Offset

    def __str__(self) -> str:
        """return a readable string representation"""
        if self.is_system_message:
            return f"[{self.sent_at.strftime('%Y-%m-%d %H:%M')}] {self.text}"

        return f"[{self.sent_at.strftime('%Y-%m-%d %H:%M')}] {self.sender}: {self.text}"

    def to_dict(self) -> dict:
        """return the message as a dictionary"""
        return {
            "sender": self.sender,
            "sent": self.sent,
            "sent_at": self.sent_at.strftime("%Y-%m-%d %H:%M"),
            "text": self.text,
            "offset": self.offset.to_dict(),
        }

    @classmethod
    def from_dict(cls, message: dict) -> "Message":
        """create a message from a dictionary"""
        return cls(
            sender=message["sender"],
            sent=message["sent"],
            sent_at=datetime.strptime(message["sent_at"], "%Y-%m-%d %H:%M"),
            text=message["text"],
            offset=Offset.from_dict(message["offset"]),
        )

    @property
    def is_system_message(self) -> bool:
        """
        Return True if this is a WhatsApp system message.

        System messages do not have a sender.
        """
        return self.sender == ""
