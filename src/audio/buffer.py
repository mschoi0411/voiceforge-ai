from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class QueueStats:
    dropped_frames: int = 0
    pushed_frames: int = 0


class BoundedFrameQueue(Generic[T]):
    def __init__(self, max_frames: int) -> None:
        if max_frames <= 0:
            raise ValueError("max_frames must be positive.")
        self._max_frames = max_frames
        self._items: deque[T] = deque()
        self.stats = QueueStats()

    @property
    def max_frames(self) -> int:
        return self._max_frames

    def depth(self) -> int:
        return len(self._items)

    def push(self, item: T) -> None:
        if len(self._items) >= self._max_frames:
            self._items.popleft()
            self.stats.dropped_frames += 1
        self._items.append(item)
        self.stats.pushed_frames += 1

    def pop(self) -> T | None:
        if not self._items:
            return None
        return self._items.popleft()

    def clear(self) -> None:
        self._items.clear()
