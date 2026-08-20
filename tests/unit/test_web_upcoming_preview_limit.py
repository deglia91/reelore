from datetime import date

from reelore.application.library_view import UpcomingEpisodeView
from reelore.web import _render_upcoming_section


def _episode(number: int) -> UpcomingEpisodeView:
    return UpcomingEpisodeView(
        media_id=f"tvmaze:{number}",
        series_title=f"Series {number}",
        season_number=1,
        episode_number=number,
        episode_title=f"Episode {number}",
        airdate=date(2026, 9, number),
        image_url=None,
    )


def test_home_upcoming_preview_shows_only_next_three_episodes() -> None:
    page = _render_upcoming_section(tuple(_episode(number) for number in range(1, 6)))

    assert "Series 1" in page
    assert "Series 2" in page
    assert "Series 3" in page
    assert "Series 4" not in page
    assert "Series 5" not in page
    assert 'href="/calendar"' in page
