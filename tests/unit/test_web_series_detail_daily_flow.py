from datetime import date

from reelore.application import TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeProgress, LibraryStatus, PersonalMediaState
from reelore.web_series_next_episode import (
    DETAIL_DEEP_LINK_SCRIPT,
    render_next_episode_callout,
)


def _caught_up_detail(status: LibraryStatus) -> TVSeriesDetailView:
    catalog = TVSeriesCatalog(
        provider_id="1",
        title="Example",
        summary=None,
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
        episodes=(),
    )
    return TVSeriesDetailView(
        media_id="tvmaze:1",
        state=PersonalMediaState("tvmaze:1", status),
        progress=EpisodeProgress("tvmaze:1"),
        catalog=catalog,
    )


def test_next_episode_callout_explains_caught_up_state() -> None:
    html = render_next_episode_callout(
        _caught_up_detail(LibraryStatus.UP_TO_DATE),
        date(2026, 8, 24),
    )

    assert "Sei in pari" in html
    assert "Nessun episodio disponibile da vedere" in html


def test_next_episode_callout_explains_completed_state() -> None:
    html = render_next_episode_callout(
        _caught_up_detail(LibraryStatus.COMPLETED),
        date(2026, 8, 24),
    )

    assert "Serie completata" in html
    assert "Hai visto tutti gli episodi disponibili" in html


def test_detail_script_restores_episode_after_seen_action() -> None:
    assert 'form[action$="/seen"]' in DETAIL_DEEP_LINK_SCRIPT
    assert "sessionStorage.setItem" in DETAIL_DEEP_LINK_SCRIPT
    assert "sessionStorage.getItem" in DETAIL_DEEP_LINK_SCRIPT
    assert "history.replaceState" in DETAIL_DEEP_LINK_SCRIPT
