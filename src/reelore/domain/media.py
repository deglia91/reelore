"""Media-agnostic domain primitives."""

from dataclasses import dataclass, replace
from enum import StrEnum


class MediaType(StrEnum):
    TV_SERIES = "tv_series"
    FILM = "film"
    BOOK = "book"
    AUDIOBOOK = "audiobook"
    MANGA = "manga"
    COMIC = "comic"


class LibraryStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    DROPPED = "dropped"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class MediaItem:
    id: str
    title: str
    media_type: MediaType

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("media id cannot be empty")
        if not self.title.strip():
            raise ValueError("media title cannot be empty")


@dataclass(frozen=True, slots=True)
class PersonalMediaState:
    media_id: str
    status: LibraryStatus = LibraryStatus.PLANNED
    completion_count: int = 0

    def __post_init__(self) -> None:
        if not self.media_id.strip():
            raise ValueError("media id cannot be empty")
        if self.completion_count < 0:
            raise ValueError("completion count cannot be negative")

    @property
    def rewatch_count(self) -> int:
        return max(0, self.completion_count - 1)

    def record_completion(self) -> "PersonalMediaState":
        return replace(
            self,
            status=LibraryStatus.COMPLETED,
            completion_count=self.completion_count + 1,
        )
