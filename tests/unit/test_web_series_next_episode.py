from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web_series_next_episode import (
    DETAIL_DEEP_LINK_SCRIPT,
    find_next_episode,
    render_next_episode_callout,
)


def _detail(progress: EpisodeProgress) -> TVSeriesDetailView:
    return TVSeriesDetailView(
        media_id="tvmaze:1",
        state=PersonalMediaState("tvmaze:1", LibraryStatus.IN_PROGRESS),
        progress=progress,
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Pilot", airdate=date(2026, 8, 1)),
                TVEpisodeMetadata("12", 1, 2, "Second", airdate=date(2026, 8, 10)),
                TVEpisodeMetadata("21", 2, 1, "Future", airdate=date(2026, 9, 1)),
            ),
        ),
    )


def test_find_next_episode_uses_first_available_unseen_episode() -> None:
    detail = _detail(EpisodeProgress("tvmaze:1").mark_seen(EpisodeRef(1, 1)))

    episode = find_next_episode(detail, date(2026, 8, 24))

    assert episode is not None
    assert (episode.season_number, episode.episode_number) == (1, 2)


def test_next_episode_callout_exposes_quick_seen_action_and_anchor() -> None:
    detail = _detail(EpisodeProgress("tvmaze:1").mark_seen(EpisodeRef(1, 1)))

    html = render_next_episode_callout(detail, date(2026, 8, 24))

    assert 'class="next-episode-callout"' in html
    assert "Prossimo episodio" in html
    assert "S01E02" in html
    assert "Second" in html
    assert 'href="#episode-s01e02"' in html
    assert 'action="/series/tvmaze:1/episodes/1/2/seen"' in html
    assert ">Visto</button>" in html


def test_next_episode_callout_shows_caught_up_state() -> None:
    progress = EpisodeProgress("tvmaze:1").mark_seen(EpisodeRef(1, 1)).mark_seen(EpisodeRef(1, 2))

    html = render_next_episode_callout(_detail(progress), date(2026, 8, 24))

    assert "Sei in pari" in html
    assert "Nessun episodio disponibile da vedere" in html


def test_detail_deep_link_script_opens_target_season() -> None:
    assert "window.location.hash" in DETAIL_DEEP_LINK_SCRIPT
    assert 'target.closest("details")' in DETAIL_DEEP_LINK_SCRIPT
    assert "details.open = true" in DETAIL_DEEP_LINK_SCRIPT
