import pytest

from reelore.domain import EpisodeProgress, EpisodeRef, MediaItem, MediaType, TVSeries


def test_tv_series_requires_tv_media_type() -> None:
    with pytest.raises(ValueError, match="tv_series"):
        TVSeries(MediaItem(id="alien", title="Alien", media_type=MediaType.FILM))


def test_episode_reference_requires_positive_numbers() -> None:
    with pytest.raises(ValueError, match="season number"):
        EpisodeRef(season_number=0, episode_number=1)

    with pytest.raises(ValueError, match="episode number"):
        EpisodeRef(season_number=1, episode_number=0)


def test_episode_progress_marks_seen_episodes_idempotently() -> None:
    episode = EpisodeRef(season_number=2, episode_number=4)
    progress = EpisodeProgress(media_id="severance")

    updated = progress.mark_seen(episode).mark_seen(episode)

    assert updated.has_seen(episode)
    assert updated.seen_count == 1
    assert progress.seen_count == 0
