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


class StubViewStore:
    def list_media(self) -> tuple[MediaItem, ...]:
        return (MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES),)

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS, completion_count=2)

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return EpisodeProgress(media_id).mark_seen(EpisodeRef(1, 1))

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        assert provider_id == "1"
        return TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary="Summary",
            status="Running",
            premiered=None,
            ended=None,
            image_url="https://img.example/poster.jpg",
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Pilot"),
                TVEpisodeMetadata("12", 1, 2, "Second"),
            ),
        )


def test_library_view_combines_catalog_tracking_and_rewatch_data() -> None:
    service = LibraryViewService(StubViewStore())

    item = service.list_items()[0]
    detail = service.get_tv_series("tvmaze:1")

    assert item.image_url == "https://img.example/poster.jpg"
    assert item.status is LibraryStatus.IN_PROGRESS
    assert item.seen_episodes == 1
    assert item.total_episodes == 2
    assert item.rewatch_count == 1
    assert detail is not None
    assert detail.catalog.title == "Example"
    assert detail.progress.has_seen(EpisodeRef(1, 1))
