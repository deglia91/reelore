"""TV-series-specific domain model."""

from dataclasses import dataclass, replace
from datetime import datetime

from reelore.domain.media import MediaItem, MediaType


@dataclass(frozen=True, slots=True, order=True)
class EpisodeRef:
    season_number: int
    episode_number: int

    def __post_init__(self) -> None:
        if self.season_number < 1:
            raise ValueError("season number must be positive")
        if self.episode_number < 1:
            raise ValueError("episode number must be positive")


@dataclass(frozen=True, slots=True)
class EpisodeWatch:
    media_id: str
    episode: EpisodeRef
    watched_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.media_id.strip():
            raise ValueError("media id cannot be empty")


@dataclass(frozen=True, slots=True)
class TVSeries:
    media: MediaItem

    def __post_init__(self) -> None:
        if self.media.media_type is not MediaType.TV_SERIES:
            raise ValueError("TVSeries requires a tv_series media item")


@dataclass(frozen=True, slots=True)
class EpisodeProgress:
    media_id: str
    seen_episodes: frozenset[EpisodeRef] = frozenset()

    def __post_init__(self) -> None:
        if not self.media_id.strip():
            raise ValueError("media id cannot be empty")

    def mark_seen(self, episode: EpisodeRef) -> "EpisodeProgress":
        return replace(self, seen_episodes=self.seen_episodes | {episode})

    def mark_unseen(self, episode: EpisodeRef) -> "EpisodeProgress":
        return replace(self, seen_episodes=self.seen_episodes - {episode})

    def has_seen(self, episode: EpisodeRef) -> bool:
        return episode in self.seen_episodes

    @property
    def seen_count(self) -> int:
        return len(self.seen_episodes)
