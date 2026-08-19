from reelore.application.catalog import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import RewatchProgressView, TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import _render_rewatch_progress


def _detail(rewatch_progress: RewatchProgressView | None) -> TVSeriesDetailView:
    media_id = "tvmaze:1"
    return TVSeriesDetailView(
        media_id=media_id,
        state=PersonalMediaState(media_id, LibraryStatus.COMPLETED),
        progress=EpisodeProgress(media_id),
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Severance",
            summary=None,
            status="Ended",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Episode 1"),
                TVEpisodeMetadata("12", 1, 2, "Episode 2"),
                TVEpisodeMetadata("13", 1, 3, "Episode 3"),
            ),
        ),
        rewatch_progress=rewatch_progress,
    )


def test_rewatch_progress_renders_current_pass_and_next_episode() -> None:
    html = _render_rewatch_progress(
        _detail(
            RewatchProgressView(
                pass_number=2,
                watched_episodes=1,
                total_episodes=3,
                next_episode=EpisodeRef(1, 2),
            )
        )
    )

    assert "Rewatch 2" in html
    assert "1/3 episodi" in html
    assert "Prossimo S01E02" in html


def test_rewatch_progress_is_hidden_without_active_rewatch() -> None:
    assert _render_rewatch_progress(_detail(None)) == ""
