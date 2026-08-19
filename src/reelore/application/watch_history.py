"""Persistence boundary for episode watch history."""

from typing import Protocol

from reelore.domain import EpisodeWatch


class WatchHistoryRepository(Protocol):
    """Append and read episode watch records without exposing storage details."""

    def record_episode_watch(self, watch: EpisodeWatch) -> None: ...

    def list_episode_watches(self, media_id: str) -> tuple[EpisodeWatch, ...]: ...
