from datetime import date

from fastapi.testclient import TestClient

from reelore.application import ImportedTVSeries, TVSearchResult, TVSeriesCatalog
from reelore.application.library_view import (
    LibraryItemView,
    RecentEpisodeView,
    TopTenItemView,
    TVSeriesDetailView,
    UpcomingEpisodeView,
)
from reelore.domain import EpisodeRef, LibraryStatus
from reelore.web import _render_episode, create_web_app


class StubImporter:
    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return ()

    def preview_series(self, provider_id: str) -> TVSeriesCatalog:
        raise AssertionError("not used")

    def import_series(self, provider_id: str) -> ImportedTVSeries:
        raise AssertionError("not used")


class StubViews:
    def list_items(self, today: date | None = None) -> tuple[LibraryItemView, ...]:
        return ()

    def list_top_ten(self) -> tuple[TopTenItemView, ...]:
        return ()

    def list_recent_episodes(self, today: date) -> tuple[RecentEpisodeView, ...]:
        return ()

    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]:
        return ()

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None:
        return None


class StubTracker:
    def __init__(self) -> None:
        self.corrected_through: list[tuple[str, EpisodeRef]] = []

    def change_status(self, media_id: str, status: LibraryStatus) -> object:
        return None

    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> object:
        return None

    def record_episode_rewatch(self, media_id: str, episode: EpisodeRef) -> object:
        return None

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> object:
        return None

    def mark_episodes_through(self, media_id: str, episode: EpisodeRef) -> object:
        self.corrected_through.append((media_id, episode))
        return None

    def mark_season_seen(self, media_id: str, season_number: int) -> object:
        return None

    def mark_season_unseen(self, media_id: str, season_number: int) -> object:
        return None

    def remove_media(self, media_id: str) -> object:
        return None


class StubTopTen:
    def assign(self, media_id: str, rank: int) -> object:
        return None

    def remove(self, media_id: str) -> object:
        return None


def test_unseen_available_episode_offers_progress_correction() -> None:
    rendered = _render_episode(
        "tvmaze:1",
        "Episode 3",
        EpisodeRef(1, 3),
        False,
        0,
        allow_through=True,
    )

    assert 'action="/series/tvmaze:1/episodes/1/3/through"' in rendered
    assert "Visti fino a qui" in rendered
    assert "Segnare come visti tutti gli episodi fino a S01E03?" in rendered


def test_seen_or_future_episode_does_not_offer_progress_correction() -> None:
    seen = _render_episode(
        "tvmaze:1",
        "Episode 3",
        EpisodeRef(1, 3),
        True,
        1,
        allow_through=True,
    )
    future = _render_episode(
        "tvmaze:1",
        "Future",
        EpisodeRef(1, 4),
        False,
        0,
        allow_through=False,
    )

    assert "/through" not in seen
    assert "/through" not in future


def test_progress_correction_route_marks_episodes_through_target() -> None:
    tracker = StubTracker()
    client = TestClient(create_web_app(StubImporter(), StubViews(), tracker, StubTopTen()))

    response = client.post(
        "/series/tvmaze:1/episodes/2/3/through",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/series/tvmaze:1"
    assert tracker.corrected_through == [("tvmaze:1", EpisodeRef(2, 3))]
