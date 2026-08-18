from pathlib import Path

from reelore.application import (
    MediaTracker,
    TVCatalogImporter,
    TVSearchResult,
    TVSeriesCatalog,
)
from reelore.domain import LibraryStatus, MediaType
from reelore.infrastructure import SQLiteLibraryRepository


class StubTVProvider:
    def __init__(self, catalog: TVSeriesCatalog) -> None:
        self.catalog = catalog

    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return (TVSearchResult(provider_id=self.catalog.provider_id, title=self.catalog.title),)

    def get_series(self, provider_id: str) -> TVSeriesCatalog:
        assert provider_id == self.catalog.provider_id
        return self.catalog


def _repository(database_path: Path) -> SQLiteLibraryRepository:
    repository = SQLiteLibraryRepository(database_path)
    repository.initialize()
    return repository


def test_catalog_import_flows_from_provider_to_local_sqlite_without_resetting_tracking(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path / "reelore.db")
    tracker = MediaTracker(repository)
    catalog = TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary="Office workers undergo a severance procedure.",
        status="Running",
        premiered=None,
        ended=None,
        image_url="https://img.example/show.jpg",
    )
    importer = TVCatalogImporter(
        StubTVProvider(catalog),
        repository,
        tracker,
        provider_name="tvmaze",
    )

    results = importer.search("Severance")
    imported = importer.import_series("16740", LibraryStatus.IN_PROGRESS)

    assert results[0].title == "Severance"
    assert imported.media_id == "tvmaze:16740"
    media = repository.get_media(imported.media_id)
    assert media is not None
    assert media.media_type is MediaType.TV_SERIES
    assert repository.get_personal_state(imported.media_id) is not None
    assert repository.get_tv_series_catalog("16740") == catalog

    completed = tracker.record_completion(imported.media_id)
    assert completed.completion_count == 1

    importer.import_series("16740", LibraryStatus.PLANNED)

    preserved = repository.get_personal_state(imported.media_id)
    assert preserved is not None
    assert preserved.status is LibraryStatus.COMPLETED
    assert preserved.completion_count == 1
