from reelore.domain import EpisodeProgress, EpisodeRef
from reelore.web import _default_open_season


def test_default_open_season_is_first_incomplete_season() -> None:
    seasons = {
        1: (EpisodeRef(1, 1), EpisodeRef(1, 2)),
        2: (EpisodeRef(2, 1), EpisodeRef(2, 2)),
        3: (EpisodeRef(3, 1),),
    }
    progress = (
        EpisodeProgress("tvmaze:1")
        .mark_seen(EpisodeRef(1, 1))
        .mark_seen(EpisodeRef(1, 2))
        .mark_seen(EpisodeRef(2, 1))
    )

    assert _default_open_season(seasons, progress) == 2


def test_default_open_season_is_latest_when_every_season_is_complete() -> None:
    seasons = {
        1: (EpisodeRef(1, 1),),
        2: (EpisodeRef(2, 1),),
    }
    progress = (
        EpisodeProgress("tvmaze:1")
        .mark_seen(EpisodeRef(1, 1))
        .mark_seen(EpisodeRef(2, 1))
    )

    assert _default_open_season(seasons, progress) == 2
