from datetime import date

from reelore.application.library_view import UpcomingEpisodeView
from reelore.web import _render_calendar_page, _render_mobile_nav


def _episode(
    *,
    airdate: date,
    season: int,
    episode: int,
    title: str,
) -> UpcomingEpisodeView:
    return UpcomingEpisodeView(
        media_id="tvmaze:1",
        series_title="The Bear",
        season_number=season,
        episode_number=episode,
        episode_title=title,
        airdate=airdate,
        image_url="https://img.example/the-bear.jpg",
    )


def test_calendar_groups_upcoming_episodes_by_day() -> None:
    today = date(2026, 8, 19)
    page = _render_calendar_page(
        (
            _episode(airdate=today, season=4, episode=1, title="Premiere"),
            _episode(airdate=today, season=4, episode=2, title="Second"),
            _episode(airdate=date(2026, 8, 21), season=4, episode=3, title="Third"),
        ),
        today,
    )

    assert 'class="calendar-page-heading"' in page
    assert "Calendario" in page
    assert "Oggi · 19 agosto" in page
    assert "Venerdì 21 agosto" in page
    assert page.count('class="calendar-day"') == 2
    assert "04x01" in page
    assert "04x02" in page
    assert "04x03" in page
    assert "Premiere" in page
    assert "Second" in page
    assert "Third" in page


def test_calendar_renders_empty_state() -> None:
    page = _render_calendar_page((), date(2026, 8, 19))

    assert "Nessuna uscita in programma" in page
    assert "Le nuove puntate delle serie che segui appariranno qui." in page


def test_mobile_navigation_links_to_dedicated_calendar() -> None:
    navigation = _render_mobile_nav()

    assert 'href="/calendar">Calendario</a>' in navigation
    assert 'href="/#upcoming">Calendario</a>' not in navigation
