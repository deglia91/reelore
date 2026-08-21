from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.availability import (
    AvailabilityProvider,
    AvailabilityType,
    SeasonAvailability,
)
from reelore.application.library_view import LibraryItemView, TVSeriesDetailView, UpcomingEpisodeView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import (
    _render_calendar_episode,
    _render_home_library_sections,
    _render_series_detail,
)


def _detail() -> TVSeriesDetailView:
    media_id = "tvmaze:1"
    return TVSeriesDetailView(
        media_id=media_id,
        state=PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS),
        progress=EpisodeProgress(media_id).mark_seen(EpisodeRef(1, 1)),
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Severance",
            summary="Office workers have divided memories.",
            status="Running",
            premiered=date(2022, 2, 18),
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Good News About Hell"),
                TVEpisodeMetadata("12", 1, 2, "Half Loop"),
            ),
        ),
    )


def test_series_detail_surfaces_next_episode_with_quick_seen_action() -> None:
    page = _render_series_detail(_detail())

    assert 'class="next-episode-callout"' in page
    assert "Prossimo episodio" in page
    assert "S01E02" in page
    assert "Half Loop" in page
    assert 'action="/series/tvmaze:1/episodes/1/2/seen"' in page
    assert ">Visto</button>" in page


def test_calendar_entry_surfaces_provider_chip_with_logo() -> None:
    entry = _render_calendar_episode(
        UpcomingEpisodeView(
            media_id="tvmaze:1",
            series_title="The Bear",
            season_number=4,
            episode_number=2,
            episode_title="Second Course",
            airdate=date(2026, 8, 22),
            image_url=None,
            availability=SeasonAvailability(
                season_number=4,
                region="IT",
                providers=(
                    AvailabilityProvider(
                        "Disney Plus",
                        AvailabilityType.STREAM,
                        logo_url="https://img.example/disney.png",
                    ),
                ),
                source="JustWatch",
            ),
        )
    )

    assert 'class="calendar-provider"' in entry
    assert 'src="https://img.example/disney.png"' in entry
    assert "Disney Plus" in entry


def test_continue_watching_prioritizes_series_with_available_next_episode() -> None:
    waiting = LibraryItemView(
        media_id="tvmaze:waiting",
        title="Waiting Show",
        status=LibraryStatus.IN_PROGRESS,
        completion_count=0,
        rewatch_count=0,
        image_url=None,
        seen_episodes=8,
        total_episodes=8,
        next_episode=None,
    )
    actionable = LibraryItemView(
        media_id="tvmaze:actionable",
        title="Actionable Show",
        status=LibraryStatus.IN_PROGRESS,
        completion_count=0,
        rewatch_count=0,
        image_url=None,
        seen_episodes=3,
        total_episodes=8,
        next_episode=None,
    )
    actionable = LibraryItemView(
        media_id=actionable.media_id,
        title=actionable.title,
        status=actionable.status,
        completion_count=actionable.completion_count,
        rewatch_count=actionable.rewatch_count,
        image_url=actionable.image_url,
        seen_episodes=actionable.seen_episodes,
        total_episodes=actionable.total_episodes,
        next_episode=__import__(
            "reelore.application.library_view", fromlist=["NextEpisodeView"]
        ).NextEpisodeView(1, 4, "Ready Now"),
    )

    html = _render_home_library_sections((waiting, actionable))

    assert html.index("Actionable Show") < html.index("Waiting Show")
