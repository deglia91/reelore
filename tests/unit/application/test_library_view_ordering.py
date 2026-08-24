from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import LibraryViewService
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)


class OrderingStore:
    def list_media(self) -> tuple[MediaItem, ...]:
        return (
            MediaItem("tvmaze:1", "Waiting Show", MediaType.TV_SERIES),
            MediaItem("tvmaze:2", "Actionable Show", MediaType.TV_SERIES),
        )

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS)

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        progress = EpisodeProgress(media_id)
        if media_id == "tvmaze:1":
            return progress.mark_seen(EpisodeRef(1, 1))
        return progress

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        episodes: tuple[TVEpisodeMetadata, ...]
        if provider_id == "1":
            episodes = (
                TVEpisodeMetadata("11", 1, 1, "Seen", airdate=date(2026, 8, 1)),
                TVEpisodeMetadata("12", 1, 2, "Future", airdate=date(2026, 9, 1)),
            )
        else:
            episodes = (TVEpisodeMetadata("21", 1, 1, "Ready", airdate=date(2026, 8, 1)),)
        return TVSeriesCatalog(
            provider_id=provider_id,
            title="Example",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=episodes,
        )


def test_library_view_prioritizes_items_with_available_next_episode() -> None:
    items = LibraryViewService(OrderingStore()).list_items(date(2026, 8, 21))

    assert [item.title for item in items] == ["Actionable Show", "Waiting Show"]
