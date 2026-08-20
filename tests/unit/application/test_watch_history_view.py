from datetime import datetime

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.watch_history_view import WatchHistoryViewService
from reelore.domain import EpisodeRef, EpisodeWatch, MediaItem, MediaType


class StubHistoryStore:
    def list_media(self) -> tuple[MediaItem, ...]:
        return (
            MediaItem("tvmaze:1", "Severance", MediaType.TV_SERIES),
            MediaItem("tvmaze:2", "The Bear", MediaType.TV_SERIES),
        )

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        catalogs = {
            "1": TVSeriesCatalog(
                provider_id="1",
                title="Severance",
                summary=None,
                status="Running",
                premiered=None,
                ended=None,
                image_url=None,
                episodes=(TVEpisodeMetadata("11", 1, 1, "Good News About Hell"),),
            ),
            "2": TVSeriesCatalog(
                provider_id="2",
                title="The Bear",
                summary=None,
                status="Running",
                premiered=None,
                ended=None,
                image_url=None,
                episodes=(TVEpisodeMetadata("23", 2, 3, "Sundae"),),
            ),
        }
        return catalogs.get(provider_id)


class StubGlobalHistory:
    def list_all_episode_watches(self) -> tuple[EpisodeWatch, ...]:
        return (
            EpisodeWatch("tvmaze:1", EpisodeRef(1, 1), datetime(2026, 8, 18, 20, 0)),
            EpisodeWatch("tvmaze:2", EpisodeRef(2, 3), datetime(2026, 8, 19, 21, 0)),
            EpisodeWatch("tvmaze:1", EpisodeRef(1, 1), datetime(2026, 8, 20, 22, 0)),
        )


def test_watch_history_view_lists_latest_watches_first_with_watch_number() -> None:
    service = WatchHistoryViewService(StubHistoryStore(), StubGlobalHistory())

    history = service.list_history()

    assert [item.series_title for item in history] == ["Severance", "The Bear", "Severance"]
    assert [item.episode_title for item in history] == ["Good News About Hell", "Sundae", "Good News About Hell"]
    assert [item.watch_number for item in history] == [2, 1, 1]
    assert history[0].season_number == 1
    assert history[0].episode_number == 1
    assert history[0].watched_at == datetime(2026, 8, 20, 22, 0)


def test_watch_history_view_ignores_orphaned_history_entries() -> None:
    class OrphanHistory:
        def list_all_episode_watches(self) -> tuple[EpisodeWatch, ...]:
            return (EpisodeWatch("tvmaze:999", EpisodeRef(1, 1)),)

    service = WatchHistoryViewService(StubHistoryStore(), OrphanHistory())

    assert service.list_history() == ()
