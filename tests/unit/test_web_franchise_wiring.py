from datetime import date
from typing import cast

from fastapi.testclient import TestClient

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import FranchiseRelationType, FranchiseTVTitle
from reelore.application.library_view import (
    LibraryItemView,
    RecentEpisodeView,
    TopTenItemView,
    TVSeriesDetailView,
    UpcomingEpisodeView,
)
from reelore.domain import EpisodeProgress, LibraryStatus, PersonalMediaState
from reelore.web import (
    TopTenTrackingService,
    TrackingService,
    TVImportService,
    create_web_app,
)


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


class RecordingFranchiseViews:
    def __init__(self, items: tuple[FranchiseTVTitle, ...]) -> None:
        self.items = items
        self.calls = 0

    def list_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]:
        self.calls += 1
        assert catalog.provider_id == "169"
        return self.items


def _detail() -> TVSeriesDetailView:
    media_id = "tvmaze:169"
    return TVSeriesDetailView(
        media_id=media_id,
        state=PersonalMediaState(media_id, LibraryStatus.COMPLETED),
        progress=EpisodeProgress(media_id),
        catalog=TVSeriesCatalog(
            provider_id="169",
            title="Breaking Bad",
            summary=None,
            status="Ended",
            premiered=date(2008, 1, 20),
            ended=date(2013, 9, 29),
            image_url=None,
        ),
    )


def test_series_detail_requests_franchise_titles_but_home_does_not() -> None:
    franchise_views = RecordingFranchiseViews(
        (
            FranchiseTVTitle(
                provider_key="618",
                title="Better Call Saul",
                relations=(
                    FranchiseRelationType.SPIN_OFF_OF,
                    FranchiseRelationType.PREQUEL_OF,
                ),
                premiered=date(2015, 2, 8),
            ),
        )
    )
    importer = cast(TVImportService, object())
    tracker = cast(TrackingService, object())
    top_ten = cast(TopTenTrackingService, object())
    client = TestClient(
        create_web_app(
            importer,
            StubViews(_detail()),
            tracker,
            top_ten,
            franchise_views=franchise_views,
        )
    )

    home = client.get("/")

    assert home.status_code == 200
    assert franchise_views.calls == 0

    detail = client.get("/series/tvmaze:169")

    assert detail.status_code == 200
    assert franchise_views.calls == 1
    assert "Franchise e collegamenti" in detail.text
    assert "Better Call Saul" in detail.text
    assert "Spin-off · Prequel · 2015" in detail.text
