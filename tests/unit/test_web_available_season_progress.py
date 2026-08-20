from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import _available_episode_refs, _default_open_season, _render_series_detail


def test_available_episode_refs_include_unknown_and_already_aired_episodes() -> None:
    episodes = (
        TVEpisodeMetadata("11", 1, 1, "Unknown", airdate=None),
        TVEpisodeMetadata("12", 1, 2, "Aired", airdate=date(2026, 8, 20)),
        TVEpisodeMetadata("13", 1, 3, "Future", airdate=date(2026, 8, 21)),
    )

    assert _available_episode_refs(episodes, date(2026, 8, 20)) == (
        EpisodeRef(1, 1),
        EpisodeRef(1, 2),
    )


def test_default_open_season_ignores_future_only_seasons() -> None:
    media_id = "tvmaze:1"
    available_episode = EpisodeRef(1, 1)
    progress = EpisodeProgress(media_id).mark_seen(available_episode)

    assert (
        _default_open_season(
            {
                1: (available_episode,),
                2: (),
            },
            progress,
        )
        == 1
    )


def test_default_open_season_is_none_when_every_season_is_future_only() -> None:
    assert _default_open_season({1: (), 2: ()}, EpisodeProgress("tvmaze:1")) is None


def test_series_detail_counts_only_available_episodes_and_opens_next_incomplete_season() -> None:
    media_id = "tvmaze:1"
    progress = EpisodeProgress(media_id).mark_seen(EpisodeRef(1, 1))
    detail = TVSeriesDetailView(
        media_id=media_id,
        state=PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS),
        progress=progress,
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Severance",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Aired", airdate=date(2020, 1, 1)),
                TVEpisodeMetadata("12", 1, 2, "Future", airdate=date(2100, 1, 1)),
                TVEpisodeMetadata("21", 2, 1, "Available", airdate=None),
            ),
        ),
    )

    page = _render_series_detail(detail)

    assert "1/2 episodi" in page
    assert "1/3 episodi" not in page
    assert "1/1 disponibili visti" in page
    assert "✓ Stagione vista" in page
    assert "Future" in page
    assert 'action="/series/tvmaze:1/episodes/1/2/seen"' not in page
    assert 'action="/series/tvmaze:1/episodes/1/2/through"' not in page
    assert page.count('class="season-details" open') == 1
    season_two = page.index("Stagione 2")
    open_details = page.index('class="season-details" open')
    assert season_two < open_details
