from datetime import date

from fastapi.testclient import TestClient

from reelore.application import (
    ImportedTVSeries,
    TVEpisodeMetadata,
    TVSearchResult,
    TVSeriesCatalog,
)
from reelore.application.library_view import LibraryItemView, TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import create_web_app


class StubImporter:
    def __init__(self) -> None:
        self.imported_ids: list[str] = []

    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        assert query == "Severance"
        return (
            TVSearchResult(
                provider_id="16740",
                title="Severance",
                premiered=date(2022, 2, 18),
                status="Running",
                image_url="https://img.example/severance.jpg",
            ),
        )

    def import_series(self, provider_id: str) -> ImportedTVSeries:
        self.imported_ids.append(provider_id)
        return ImportedTVSeries(
            media_id=f"tvmaze:{provider_id}",
            catalog=_catalog(provider_id),
        )


class StubViews:
    def list_items(self) -> tuple[LibraryItemView, ...]:
        return (
            LibraryItemView(
                media_id="tvmaze:1",
                title="The Bear",
                status=LibraryStatus.IN_PROGRESS,
                completion_count=0,
                rewatch_count=0,
                image_url="https://img.example/the-bear.jpg",
                seen_episodes=1,
                total_episodes=2,
            ),
        )

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None:
        return TVSeriesDetailView(
            media_id=media_id,
            state=PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS),
            progress=EpisodeProgress(media_id).mark_seen(EpisodeRef(1, 1)),
            catalog=_catalog("1"),
        )


class StubTracker:
    def __init__(self) -> None:
        self.seen: list[tuple[str, EpisodeRef]] = []
        self.unseen: list[tuple[str, EpisodeRef]] = []

    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> object:
        self.seen.append((media_id, episode))
        return object()

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> object:
        self.unseen.append((media_id, episode))
        return object()


def _catalog(provider_id: str) -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id=provider_id,
        title="Severance",
        summary="Office workers have divided memories.",
        status="Running",
        premiered=None,
        ended=None,
        image_url="https://img.example/poster.jpg",
        episodes=(
            TVEpisodeMetadata("11", 1, 1, "Good News About Hell"),
            TVEpisodeMetadata("12", 1, 2, "Half Loop"),
        ),
    )


def test_home_renders_library_metadata_and_search_results() -> None:
    client = TestClient(create_web_app(StubImporter(), StubViews(), StubTracker()))

    response = client.get("/?q=Severance")

    assert response.status_code == 200
    assert "The Bear" in response.text
    assert "1/2 episodi" in response.text
    assert "https://img.example/the-bear.jpg" in response.text
    assert "Severance" in response.text


def test_add_series_imports_selection_and_redirects_detail() -> None:
    importer = StubImporter()
    client = TestClient(create_web_app(importer, StubViews(), StubTracker()))

    response = client.post("/series/16740/add", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/series/tvmaze:16740"
    assert importer.imported_ids == ["16740"]


def test_series_detail_renders_episodes_and_updates_progress() -> None:
    tracker = StubTracker()
    client = TestClient(create_web_app(StubImporter(), StubViews(), tracker))

    detail = client.get("/series/tvmaze:1")
    marked = client.post(
        "/series/tvmaze:1/episodes/1/2/seen",
        follow_redirects=False,
    )

    assert detail.status_code == 200
    assert "Stagione 1" in detail.text
    assert "Good News About Hell" in detail.text
    assert "Visto ✓" in detail.text
    assert marked.status_code == 303
    assert tracker.seen == [("tvmaze:1", EpisodeRef(1, 2))]
