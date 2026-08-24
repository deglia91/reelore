from datetime import date

from fastapi.testclient import TestClient

from reelore.application import ImportedTVSeries, TVSearchResult, TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import create_web_app
from reelore.web_series_next_episode import render_next_episode_callout


class EmptyImporter:
    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return ()

    def preview_series(self, provider_id: str) -> TVSeriesCatalog:
        raise AssertionError("not used")

    def import_series(self, provider_id: str) -> ImportedTVSeries:
        raise AssertionError("not used")


class EmptyViews:
    def list_items(self, today: date | None = None) -> tuple[object, ...]:
        return ()

    def list_top_ten(self) -> tuple[object, ...]:
        return ()

    def list_recent_episodes(self, today: date) -> tuple[object, ...]:
        return ()

    def list_upcoming_episodes(self, today: date) -> tuple[object, ...]:
        return ()

    def get_tv_series(self, media_id: str) -> None:
        return None


class TrackingStub:
    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> object:
        return object()

    def __getattr__(self, name: str) -> object:
        return lambda *args, **kwargs: object()


class TopTenStub:
    def assign(self, media_id: str, rank: int) -> object:
        return object()

    def remove(self, media_id: str) -> object:
        return object()


def _caught_up_detail(status: LibraryStatus) -> TVSeriesDetailView:
    catalog = TVSeriesCatalog(
        provider_id="1",
        title="Example",
        summary=None,
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
        episodes=(),
    )
    return TVSeriesDetailView(
        media_id="tvmaze:1",
        state=PersonalMediaState("tvmaze:1", status),
        progress=EpisodeProgress("tvmaze:1"),
        catalog=catalog,
    )


def test_next_episode_callout_explains_caught_up_state() -> None:
    html = render_next_episode_callout(
        _caught_up_detail(LibraryStatus.UP_TO_DATE),
        date(2026, 8, 24),
    )

    assert "Sei in pari" in html
    assert "Nessun episodio disponibile da vedere" in html


def test_next_episode_callout_explains_completed_state() -> None:
    html = render_next_episode_callout(
        _caught_up_detail(LibraryStatus.COMPLETED),
        date(2026, 8, 24),
    )

    assert "Serie completata" in html
    assert "Hai visto tutti gli episodi disponibili" in html


def test_mark_seen_returns_to_episode_anchor() -> None:
    client = TestClient(
        create_web_app(
            EmptyImporter(),
            EmptyViews(),
            TrackingStub(),
            TopTenStub(),
        )
    )

    response = client.post(
        "/series/tvmaze:1/episodes/2/3/seen",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/series/tvmaze:1#episode-s02e03"
