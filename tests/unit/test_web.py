from datetime import date

from fastapi.testclient import TestClient

from reelore.application import (
    ImportedTVSeries,
    TVEpisodeMetadata,
    TVSearchResult,
    TVSeriesCatalog,
)
from reelore.application.availability import (
    AvailabilityProvider,
    AvailabilityType,
    SeasonAvailability,
)
from reelore.application.library_view import (
    LibraryItemView,
    NextEpisodeView,
    TVSeriesDetailView,
    UpcomingEpisodeView,
)
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
    def list_items(self, today: date | None = None) -> tuple[LibraryItemView, ...]:
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
                next_episode=NextEpisodeView(1, 2, "Second Course"),
            ),
            LibraryItemView(
                media_id="tvmaze:2",
                title="Severance",
                status=LibraryStatus.UP_TO_DATE,
                completion_count=0,
                rewatch_count=0,
                image_url="https://img.example/severance.jpg",
                seen_episodes=2,
                total_episodes=2,
            ),
            LibraryItemView(
                media_id="tvmaze:3",
                title="Breaking Bad",
                status=LibraryStatus.COMPLETED,
                completion_count=1,
                rewatch_count=0,
                image_url="https://img.example/breaking-bad.jpg",
                seen_episodes=62,
                total_episodes=62,
            ),
        )

    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]:
        return (
            UpcomingEpisodeView(
                media_id="tvmaze:2",
                series_title="Severance",
                season_number=3,
                episode_number=1,
                episode_title="Future Episode",
                airdate=date(2027, 1, 10),
                image_url="https://img.example/future.jpg",
            ),
        )

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None:
        return TVSeriesDetailView(
            media_id=media_id,
            state=PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS),
            progress=EpisodeProgress(media_id).mark_seen(EpisodeRef(1, 1)),
            catalog=_catalog("1"),
            availability=(
                SeasonAvailability(
                    season_number=1,
                    region="IT",
                    providers=(AvailabilityProvider("Apple TV Plus", AvailabilityType.STREAM),),
                    source="JustWatch",
                    source_url="https://example.test/watch",
                ),
            ),
        )


class StubTracker:
    def __init__(self) -> None:
        self.seen: list[tuple[str, EpisodeRef]] = []
        self.unseen: list[tuple[str, EpisodeRef]] = []
        self.statuses: list[tuple[str, LibraryStatus]] = []
        self.completions: list[str] = []

    def change_status(self, media_id: str, status: LibraryStatus) -> object:
        self.statuses.append((media_id, status))
        return object()

    def record_completion(self, media_id: str) -> object:
        self.completions.append(media_id)
        return object()

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


def test_home_renders_tracking_upcoming_and_search_sections() -> None:
    client = TestClient(create_web_app(StubImporter(), StubViews(), StubTracker()))

    response = client.get("/?q=Severance")

    assert response.status_code == 200
    assert "Prossime uscite" in response.text
    assert "S03E01" in response.text
    assert "10/01/2027" in response.text
    assert "Future Episode" in response.text
    assert "Continua a guardare" in response.text
    assert "S01E02" in response.text
    assert "Second Course" in response.text
    assert "Segna visto" in response.text
    assert "In pari" in response.text
    assert "La tua libreria" in response.text
    assert "The Bear" in response.text
    assert "1/2 episodi" in response.text
    assert "Breaking Bad" in response.text
    assert "https://img.example/the-bear.jpg" in response.text
    assert "Severance" in response.text


def test_home_quick_action_marks_next_episode_seen_and_returns_home() -> None:
    tracker = StubTracker()
    client = TestClient(create_web_app(StubImporter(), StubViews(), tracker))

    response = client.post(
        "/series/tvmaze:1/episodes/1/2/seen/home",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert tracker.seen == [("tvmaze:1", EpisodeRef(1, 2))]


def test_add_series_imports_selection_and_redirects_detail() -> None:
    importer = StubImporter()
    client = TestClient(create_web_app(importer, StubViews(), StubTracker()))

    response = client.post("/series/16740/add", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/series/tvmaze:16740"
    assert importer.imported_ids == ["16740"]


def test_series_detail_renders_episodes_availability_and_updates_progress() -> None:
    tracker = StubTracker()
    client = TestClient(create_web_app(StubImporter(), StubViews(), tracker))

    detail = client.get("/series/tvmaze:1")
    marked = client.post(
        "/series/tvmaze:1/episodes/1/2/seen",
        follow_redirects=False,
    )

    assert detail.status_code == 200
    assert "Stagione 1" in detail.text
    assert "Disponibile in Italia" in detail.text
    assert "Apple TV Plus" in detail.text
    assert "streaming" in detail.text
    assert "JustWatch" in detail.text
    assert "Good News About Hell" in detail.text
    assert "Visto ✓" in detail.text
    assert marked.status_code == 303
    assert tracker.seen == [("tvmaze:1", EpisodeRef(1, 2))]


def test_series_detail_changes_personal_status_and_records_completion() -> None:
    tracker = StubTracker()
    client = TestClient(create_web_app(StubImporter(), StubViews(), tracker))

    status_response = client.post(
        "/series/tvmaze:1/status",
        data={"status": "dropped"},
        follow_redirects=False,
    )
    completion_response = client.post(
        "/series/tvmaze:1/completion",
        follow_redirects=False,
    )

    assert status_response.status_code == 303
    assert completion_response.status_code == 303
    assert tracker.statuses == [("tvmaze:1", LibraryStatus.DROPPED)]
    assert tracker.completions == ["tvmaze:1"]
