"""FIFO `Message`s cache."""

from .datastructs import Message


# message index -> message
class MessageCache:
    """A FIFO cache for `Message`s."""

    # faster attribute access and memory optimization
    __slots__ = ("capacity", "cache")

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[int, Message] = {}

    def __getitem__(self, index: int) -> Message:
        """get a `Message` by index"""
        return self.cache[index]

    def __setitem__(self, index: int, message: Message):
        """set a `Message` by index"""
        if len(self.cache) >= self.capacity:
            # remove the oldest message
            self.cache.pop(next(iter(self.cache)))

        self.cache[index] = message

    def __len__(self) -> int:
        """return the number of messages in the cache"""
        return len(self.cache)

    def __contains__(self, index: int) -> bool:
        """return whether the cache contains a `Message` by index"""
        return index in self.cache

    def clear(self):
        """clear the cache"""
        self.cache.clear()
