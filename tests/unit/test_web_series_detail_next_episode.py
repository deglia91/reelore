from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import _render_series_detail


def test_series_detail_composes_next_episode_callout_and_deep_link_behavior() -> None:
    detail = TVSeriesDetailView(
        media_id="tvmaze:1",
        state=PersonalMediaState("tvmaze:1", LibraryStatus.IN_PROGRESS),
        progress=EpisodeProgress("tvmaze:1").mark_seen(EpisodeRef(1, 1)),
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary="Summary",
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Pilot", airdate=date(2026, 1, 1)),
                TVEpisodeMetadata("12", 1, 2, "Second", airdate=date(2026, 1, 8)),
            ),
        ),
    )

    html = _render_series_detail(detail)

    assert 'class="next-episode-callout"' in html
    assert "Prossimo episodio" in html
    assert 'href="#episode-s01e02"' in html
    assert 'action="/series/tvmaze:1/episodes/1/2/seen"' in html
    assert 'id="episode-s01e02"' in html
    assert "details.open = true" in html
