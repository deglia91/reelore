from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.watch_statistics import WatchStatisticsService
from reelore.domain import EpisodeRef, EpisodeWatch


class StatisticsStoreStub:
    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        if provider_id != "1":
            return None
        return TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Pilot", runtime_minutes=50),
                TVEpisodeMetadata("12", 1, 2, "Second", runtime_minutes=30),
                TVEpisodeMetadata("13", 1, 3, "Unknown"),
            ),
        )


class HistoryStub:
    def __init__(self, watches: tuple[EpisodeWatch, ...]) -> None:
        self._watches = watches

    def list_all_episode_watches(self) -> tuple[EpisodeWatch, ...]:
        return self._watches


def test_statistics_count_rewatches_in_total_watch_time() -> None:
    service = WatchStatisticsService(
        StatisticsStoreStub(),
        HistoryStub(
            (
                EpisodeWatch("tvmaze:1", EpisodeRef(1, 1)),
                EpisodeWatch("tvmaze:1", EpisodeRef(1, 2)),
                EpisodeWatch("tvmaze:1", EpisodeRef(1, 1)),
            )
        ),
    )

    statistics = service.get_statistics()

    assert statistics.total_watch_minutes == 130
    assert statistics.total_watches == 3
    assert statistics.unique_episodes == 2
    assert statistics.rewatches == 1


def test_statistics_keep_unknown_runtime_watch_in_activity_counts() -> None:
    service = WatchStatisticsService(
        StatisticsStoreStub(),
        HistoryStub((EpisodeWatch("tvmaze:1", EpisodeRef(1, 3)),)),
    )

    statistics = service.get_statistics()

    assert statistics.total_watch_minutes == 0
    assert statistics.total_watches == 1
    assert statistics.unique_episodes == 1
    assert statistics.rewatches == 0
