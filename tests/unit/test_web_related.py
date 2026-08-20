from datetime import date
from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

import reelore.bootstrap as bootstrap
from reelore.application.catalog import TVSeriesCatalog
from reelore.application.library_view import (
    LibraryItemView,
    RecentEpisodeView,
    TopTenItemView,
    TVSeriesDetailView,
    UpcomingEpisodeView,
)
from reelore.application.related import RelatedTVTitle
from reelore.domain import EpisodeProgress, LibraryStatus, PersonalMediaState
from reelore.web import (
    TVImportService,
    TopTenTrackingService,
    TrackingService,
    create_web_app,
)
from reelore.web_related import render_related_titles


class StubViews:
    def __init__(self, detail: TVSeriesDetailView) -> None:
        self._detail = detail

    def list_items(self, today: date | None = None) -> tuple[LibraryItemView, ...]:
        return ()

    def list_top_ten(self) -> tuple[TopTenItemView, ...]:
        return ()

    def list_recent_episodes(self, today: date) -> tuple[RecentEpisodeView, ...]:
        return ()

    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]:
        return ()

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None:
        return self._detail if media_id == self._detail.media_id else None


class RecordingRelatedViews:
    def __init__(self, items: tuple[RelatedTVTitle, ...]) -> None:
        self.items = items
        self.calls = 0

    def list_for(self, catalog: TVSeriesCatalog) -> tuple[RelatedTVTitle, ...]:
        self.calls += 1
        assert catalog.title == "Loki"
        return self.items


class FakeRelatedProvider:
    created_with: list[str] = []

    def __init__(self, token: str) -> None:
        self.created_with.append(token)

    def related_to(self, catalog: TVSeriesCatalog) -> tuple[RelatedTVTitle, ...]:
        return ()


def _detail() -> TVSeriesDetailView:
    media_id = "tvmaze:1"
    return TVSeriesDetailView(
        media_id=media_id,
        state=PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS),
        progress=EpisodeProgress(media_id),
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Loki",
            summary=None,
            status="Ended",
            premiered=None,
            ended=None,
            image_url=None,
        ),
    )


def _web_app(
    views: StubViews,
    related_views: RecordingRelatedViews | None = None,
) -> TestClient:
    importer = cast(TVImportService, object())
    tracker = cast(TrackingService, object())
    top_ten = cast(TopTenTrackingService, object())
    app = create_web_app(importer, views, tracker, top_ten, related_views)
    return TestClient(app)


def test_related_title_renderer_limits_compact_preview_to_four_items() -> None:
    related = tuple(
        RelatedTVTitle(
            provider_key=str(index),
            title=f"Related {index}",
            premiered=date(2020 + index, 1, 1),
            image_url=f"https://img.example/{index}.jpg",
        )
        for index in range(1, 6)
    )

    page = render_related_titles(related)

    assert "Titoli collegati" in page
    for index in range(1, 5):
        assert f"Related {index}" in page
        assert f"https://img.example/{index}.jpg" in page
    assert "Related 5" not in page
    assert 'class="grid related-titles-rail"' in page


def test_related_title_renderer_hides_empty_section() -> None:
    assert render_related_titles(()) == ""


def test_series_detail_requests_related_titles_but_home_does_not() -> None:
    related = (RelatedTVTitle(provider_key="2", title="Moon Knight"),)
    related_views = RecordingRelatedViews(related)
    client = _web_app(StubViews(_detail()), related_views)

    home = client.get("/")

    assert home.status_code == 200
    assert related_views.calls == 0

    detail = client.get("/series/tvmaze:1")

    assert detail.status_code == 200
    assert related_views.calls == 1
    assert "Titoli collegati" in detail.text
    assert "Moon Knight" in detail.text


def test_series_detail_remains_available_without_related_provider() -> None:
    client = _web_app(StubViews(_detail()))

    response = client.get("/series/tvmaze:1")

    assert response.status_code == 200
    assert "Loki" in response.text
    assert "Titoli collegati" not in response.text


def test_bootstrap_constructs_related_provider_only_with_tmdb_token(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    FakeRelatedProvider.created_with = []
    monkeypatch.setattr(bootstrap, "TMDBRelatedTVProvider", FakeRelatedProvider)

    bootstrap.build_app(tmp_path / "without-token.db")
    assert FakeRelatedProvider.created_with == []

    bootstrap.build_app(tmp_path / "with-token.db", tmdb_token="tmdb-token")
    assert FakeRelatedProvider.created_with == ["tmdb-token"]
