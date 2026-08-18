"""Application use cases for the personal media tracker."""

from reelore.application.library import LibraryRepository
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, MediaItem, PersonalMediaState


class MediaNotFoundError(LookupError):
    """Raised when a tracking operation targets media outside the library."""


class MediaTracker:
    """Coordinate personal tracking use cases through the library repository port."""

    def __init__(self, repository: LibraryRepository) -> None:
        self._repository = repository

    def add_media(self, media: MediaItem, status: LibraryStatus = LibraryStatus.PLANNED) -> None:
        self._repository.save_media(media)
        if self._repository.get_personal_state(media.id) is None:
            self._repository.save_personal_state(
                PersonalMediaState(media_id=media.id, status=status)
            )

    def change_status(self, media_id: str, status: LibraryStatus) -> PersonalMediaState:
        state = self._require_state(media_id).change_status(status)
        self._repository.save_personal_state(state)
        return state

    def record_completion(self, media_id: str) -> PersonalMediaState:
        state = self._require_state(media_id).record_completion()
        self._repository.save_personal_state(state)
        return state

    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        self._require_media(media_id)
        progress = self._repository.get_episode_progress(media_id).mark_seen(episode)
        self._repository.save_episode_progress(progress)
        return progress

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        self._require_media(media_id)
        progress = self._repository.get_episode_progress(media_id).mark_unseen(episode)
        self._repository.save_episode_progress(progress)
        return progress

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        self._require_media(media_id)
        return self._repository.get_episode_progress(media_id)

    def _require_media(self, media_id: str) -> MediaItem:
        media = self._repository.get_media(media_id)
        if media is None:
            raise MediaNotFoundError(media_id)
        return media

    def _require_state(self, media_id: str) -> PersonalMediaState:
        self._require_media(media_id)
        state = self._repository.get_personal_state(media_id)
        if state is None:
            raise MediaNotFoundError(media_id)
        return state
