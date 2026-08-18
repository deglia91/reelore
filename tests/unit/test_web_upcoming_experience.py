from datetime import date

from reelore.application.library_view import UpcomingEpisodeView
from reelore.web import _render_upcoming_section


def test_upcoming_releases_use_a_dedicated_vertical_timeline() -> None:
    episodes = (
        UpcomingEpisodeView(
            media_id="tvmaze:2",
            series_title="Severance",
            season_number=3,
            episode_number=1,
            episode_title="Future Episode",
            airdate=date(2027, 1, 10),
            image_url="https://img.example/future.jpg",
        ),
        UpcomingEpisodeView(
            media_id="tvmaze:1",
            series_title="The Bear",
            season_number=5,
            episode_number=2,
            episode_title="Second Serving",
            airdate=date(2027, 1, 14),
            image_url="https://img.example/the-bear.jpg",
        ),
    )

    rendered = _render_upcoming_section(episodes)

    assert 'class="upcoming-list"' in rendered
    assert rendered.count('class="upcoming-item"') == 2
    assert '<time class="upcoming-date" datetime="2027-01-10">' in rendered
    assert '<span class="upcoming-day">10</span>' in rendered
    assert '<span class="upcoming-month">GEN</span>' in rendered
    assert "S03E01" in rendered
    assert "Future Episode" in rendered
