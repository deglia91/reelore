import pytest

from reelore.domain import LibraryStatus, MediaItem, MediaType, PersonalMediaState


def test_media_item_requires_identity_and_title() -> None:
    with pytest.raises(ValueError, match="media id"):
        MediaItem(id=" ", title="Breaking Bad", media_type=MediaType.TV_SERIES)

    with pytest.raises(ValueError, match="media title"):
        MediaItem(id="breaking-bad", title=" ", media_type=MediaType.TV_SERIES)


def test_personal_state_tracks_completions_and_rewatches() -> None:
    state = PersonalMediaState(media_id="breaking-bad")

    first_completion = state.record_completion()
    third_completion = first_completion.record_completion().record_completion()

    assert first_completion.status is LibraryStatus.COMPLETED
    assert first_completion.completion_count == 1
    assert first_completion.rewatch_count == 0
    assert third_completion.completion_count == 3
    assert third_completion.rewatch_count == 2


def test_completion_count_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="completion count"):
        PersonalMediaState(media_id="breaking-bad", completion_count=-1)
