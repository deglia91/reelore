from reelore.application.catalog import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import _render_series_detail


def test_series_detail_renders_episode_watch_count() -> None:
    media_id = "tvmaze:1"
    episode = EpisodeRef(1, 1)
    detail = TVSeriesDetailView(
        media_id=media_id,
        state=PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS),
        progress=EpisodeProgress(media_id).mark_seen(episode),
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(TVEpisodeMetadata("11", 1, 1, "Pilot"),),
        ),
        episode_watch_counts=((episode, 2),),
    )

    html = _render_series_detail(detail)

    assert 'class="episode-watch-count">2x</small>' in html
    assert ">Visto ✓</button>" in html
