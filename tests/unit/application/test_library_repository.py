from reelore.application import LibraryRepository


def _accepts_repository(repository: LibraryRepository) -> LibraryRepository:
    return repository


def test_library_repository_is_an_application_port() -> None:
    assert LibraryRepository is not None
    assert callable(_accepts_repository)
