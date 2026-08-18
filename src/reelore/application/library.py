"""Persistence boundaries for a personal media library."""

from typing import Protocol

from reelore.domain import EpisodeProgress, MediaItem, PersonalMediaState


class LibraryRepository(Protocol):
    """Store and restore Reelore's authoritative personal tracking state."""

    def save_media(self, media: MediaItem) -> None: ...

    def get_media(self, media_id: str) -> MediaItem | None: ...

    def save_personal_state(self, state: PersonalMediaState) -> None: ...

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None: ...

    def save_episode_progress(self, progress: EpisodeProgress) -> None: ...

    def get_episode_progress(self, media_id: str) -> EpisodeProgress: ...


class LibraryReader(Protocol):
    """Read the user's media library without exposing persistence details."""

    def list_media(self) -> tuple[MediaItem, ...]: ...
