"""Persistence boundary for episode watch history."""

from typing import Protocol

from reelore.domain import EpisodeRef, EpisodeWatch


class WatchHistoryRepository(Protocol):
    """Append and read episode watch records without exposing storage details."""

    def record_episode_watch(self, watch: EpisodeWatch) -> None: ...

    def list_episode_watches(self, media_id: str) -> tuple[EpisodeWatch, ...]: ...

    def list_all_episode_watches(self) -> tuple[EpisodeWatch, ...]: ...

    def retract_latest_episode_watch(self, media_id: str, episode: EpisodeRef) -> bool: ...
