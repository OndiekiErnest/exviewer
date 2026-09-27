"""Dataclasses for handling files."""

from dataclasses import asdict, dataclass
from functools import total_ordering


@total_ordering
@dataclass(slots=True, kw_only=True)
class FileInfo:
    """A dataclass for storing file information."""

    name: str  # base name
    path: str  # full path
    progress: int  # number of messages read from the file

    def __str__(self) -> str:
        return f"{self.name} - {self.progress} read"

    def __eq__(self, other):
        """compare FileInfo objects based on their path"""
        if isinstance(other, FileInfo):
            return self.path == other.path

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, FileInfo):
            return self.path < other.path

        return NotImplemented

    def __hash__(self):
        """hash FileInfo objects based on their path"""
        return hash(self.path)

    def to_dict(self):
        """convert FileInfo to a dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """create a FileInfo object from a dictionary"""
        name = data["name"]
        path = data["path"]
        progress = data["progress"]

        return cls(name=name, path=path, progress=progress)
