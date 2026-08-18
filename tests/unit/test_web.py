from datetime import date

from fastapi.testclient import TestClient

from reelore.application import ImportedTVSeries, TVSearchResult, TVSeriesCatalog
from reelore.domain import MediaItem, MediaType
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
            catalog=TVSeriesCatalog(
                provider_id=provider_id,
                title="Severance",
                summary=None,
                status="Running",
                premiered=None,
                ended=None,
                image_url=None,
            ),
        )


class StubLibrary:
    def list_media(self) -> tuple[MediaItem, ...]:
        return (MediaItem(id="the-bear", title="The Bear", media_type=MediaType.TV_SERIES),)


def test_home_renders_library_and_search_results() -> None:
    client = TestClient(create_web_app(StubImporter(), StubLibrary()))

    response = client.get("/?q=Severance")

    assert response.status_code == 200
    assert "Reelore" in response.text
    assert "The Bear" in response.text
    assert "Severance" in response.text
    assert "https://img.example/severance.jpg" in response.text


def test_add_series_imports_selection_and_redirects_home() -> None:
    importer = StubImporter()
    client = TestClient(create_web_app(importer, StubLibrary()))

    response = client.post("/series/16740/add", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert importer.imported_ids == ["16740"]
