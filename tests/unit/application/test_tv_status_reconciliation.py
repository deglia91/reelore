from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.tv_status_reconciliation import TVStatusReconciliationService
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)


class StubStore:
    def __init__(self, *, future_only: bool) -> None:
        self.future_only = future_only

    def list_media(self) -> tuple[MediaItem, ...]:
        return (MediaItem("tvmaze:1", "Returning", MediaType.TV_SERIES),)

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return PersonalMediaState(media_id, LibraryStatus.COMPLETED, completion_count=1)

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return EpisodeProgress(media_id).mark_seen(EpisodeRef(1, 1))

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        new_airdate = date(2026, 9, 1) if self.future_only else date(2026, 8, 20)
        return TVSeriesCatalog(
            provider_id=provider_id,
            title="Returning",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Old finale", airdate=date(2026, 1, 1)),
                TVEpisodeMetadata("21", 2, 1, "New episode", airdate=new_airdate),
            ),
        )


class StubStatusUpdater:
    def __init__(self) -> None:
        self.changes: list[tuple[str, LibraryStatus]] = []

    def change_status(self, media_id: str, status: LibraryStatus) -> PersonalMediaState:
        self.changes.append((media_id, status))
        return PersonalMediaState(media_id, status, completion_count=1)


def test_completed_series_with_only_future_unseen_episodes_returns_up_to_date() -> None:
    updater = StubStatusUpdater()
    service = TVStatusReconciliationService(StubStore(future_only=True), updater)

    result = service.reconcile(date(2026, 8, 21))

    assert updater.changes == [("tvmaze:1", LibraryStatus.UP_TO_DATE)]
    assert result.reopened == 1


def test_completed_series_with_available_unseen_episode_returns_in_progress() -> None:
    updater = StubStatusUpdater()
    service = TVStatusReconciliationService(StubStore(future_only=False), updater)

    result = service.reconcile(date(2026, 8, 21))

    assert updater.changes == [("tvmaze:1", LibraryStatus.IN_PROGRESS)]
    assert result.reopened == 1
