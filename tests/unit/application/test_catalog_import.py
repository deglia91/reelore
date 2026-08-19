from reelore.application import (
    ImportedTVSeries,
    MediaTracker,
    TVCatalogImporter,
    TVCatalogStore,
    TVSearchResult,
    TVSeriesCatalog,
)
from reelore.domain import EpisodeProgress, LibraryStatus, MediaItem, PersonalMediaState


class StubProvider:
    def __init__(self, catalog: TVSeriesCatalog) -> None:
        self.catalog = catalog

    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return (TVSearchResult(provider_id=self.catalog.provider_id, title=query.strip()),)

    def get_series(self, provider_id: str) -> TVSeriesCatalog:
        assert provider_id == self.catalog.provider_id
        return self.catalog


class MemoryRepository:
    def __init__(self) -> None:
        self.media: dict[str, MediaItem] = {}
        self.states: dict[str, PersonalMediaState] = {}
        self.progress: dict[str, EpisodeProgress] = {}

    def save_media(self, media: MediaItem) -> None:
        self.media[media.id] = media

    def get_media(self, media_id: str) -> MediaItem | None:
        return self.media.get(media_id)

    def save_personal_state(self, state: PersonalMediaState) -> None:
        self.states[state.media_id] = state

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return self.states.get(media_id)

    def save_episode_progress(self, progress: EpisodeProgress) -> None:
        self.progress[progress.media_id] = progress

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return self.progress.get(media_id, EpisodeProgress(media_id=media_id))


class MemoryCatalogStore(TVCatalogStore):
    def __init__(self) -> None:
        self.catalogs: dict[str, TVSeriesCatalog] = {}

    def save_tv_series_catalog(self, catalog: TVSeriesCatalog) -> None:
        self.catalogs[catalog.provider_id] = catalog

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        return self.catalogs.get(provider_id)


def _catalog() -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary="Office workers have divided memories.",
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
    )


def test_catalog_importer_previews_series_without_persisting_personal_state() -> None:
    catalog = _catalog()
    repository = MemoryRepository()
    store = MemoryCatalogStore()
    importer = TVCatalogImporter(
        StubProvider(catalog),
        store,
        MediaTracker(repository),
        provider_name="TVMaze",
    )

    preview = importer.preview_series("16740")

    assert preview == catalog
    assert repository.media == {}
    assert repository.states == {}
    assert store.catalogs == {}


def test_catalog_importer_imports_series_and_initializes_tracking_state() -> None:
    catalog = _catalog()
    repository = MemoryRepository()
    store = MemoryCatalogStore()
    importer = TVCatalogImporter(
        StubProvider(catalog),
        store,
        MediaTracker(repository),
        provider_name="TVMaze",
    )

    imported = importer.import_series("16740", LibraryStatus.IN_PROGRESS)

    assert imported == ImportedTVSeries(media_id="tvmaze:16740", catalog=catalog)
    assert repository.media["tvmaze:16740"].title == "Severance"
    assert repository.states["tvmaze:16740"].status is LibraryStatus.IN_PROGRESS
    assert store.get_tv_series_catalog("16740") == catalog
