import pytest

from reelore.domain import LibraryStatus, MediaItem, MediaType, PersonalMediaState


def test_media_item_requires_identity_and_title() -> None:
    with pytest.raises(ValueError, match="media id"):
        MediaItem(id=" ", title="Severance", media_type=MediaType.TV_SERIES)

    with pytest.raises(ValueError, match="media title"):
        MediaItem(id="severance", title=" ", media_type=MediaType.TV_SERIES)


def test_personal_state_tracks_rewatches_after_first_completion() -> None:
    state = PersonalMediaState(media_id="severance")

    state = state.record_completion().record_completion().record_completion()

    assert state.status is LibraryStatus.COMPLETED
    assert state.completion_count == 3
    assert state.rewatch_count == 2


def test_personal_state_changes_library_status_without_losing_completions() -> None:
    state = PersonalMediaState(media_id="severance", completion_count=2)

    updated = state.change_status(LibraryStatus.IN_PROGRESS)

    assert updated.status is LibraryStatus.IN_PROGRESS
    assert updated.completion_count == 2
