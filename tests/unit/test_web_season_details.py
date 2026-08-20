from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, PersonalMediaState
from reelore.web import _render_series_detail


def test_series_detail_opens_first_incomplete_season_and_collapses_others() -> None:
    media_id = "tvmaze:1"
    progress = (
        EpisodeProgress(media_id)
        .mark_seen(EpisodeRef(1, 1))
        .mark_seen(EpisodeRef(1, 2))
        .mark_seen(EpisodeRef(2, 1))
    )
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
                TVEpisodeMetadata("11", 1, 1, "One"),
                TVEpisodeMetadata("12", 1, 2, "Two"),
                TVEpisodeMetadata("21", 2, 1, "Three"),
                TVEpisodeMetadata("22", 2, 2, "Four"),
                TVEpisodeMetadata("31", 3, 1, "Five"),
            ),
        ),
    )

    page = _render_series_detail(detail)

    assert page.count('class="season-details"') == 3
    assert page.count('class="season-details" open') == 1
    season_two = page.index("Stagione 2")
    open_details = page.index('class="season-details" open')
    season_three = page.index("Stagione 3")
    assert season_two < open_details < season_three
    assert "Episodi e disponibilità" in page
    assert "Segna stagione vista" in page
