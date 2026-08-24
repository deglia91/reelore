from datetime import date

from reelore.application.availability import (
    AvailabilityProvider,
    AvailabilityType,
    SeasonAvailability,
)
from reelore.application.library_view import UpcomingEpisodeView
from reelore.web import _render_calendar_page, _render_mobile_nav


def _episode(
    *,
    airdate: date,
    season: int,
    episode: int,
    title: str,
    availability: SeasonAvailability | None = None,
) -> UpcomingEpisodeView:
    return UpcomingEpisodeView(
        media_id="tvmaze:1",
        series_title="The Bear",
        season_number=season,
        episode_number=episode,
        episode_title=title,
        airdate=airdate,
        image_url="https://img.example/the-bear.jpg",
        availability=availability,
    )


def test_calendar_groups_upcoming_episodes_by_day() -> None:
    today = date(2026, 8, 19)
    page = _render_calendar_page(
        (
            _episode(airdate=today, season=4, episode=1, title="Premiere"),
            _episode(airdate=today, season=4, episode=2, title="Second"),
            _episode(airdate=date(2026, 8, 20), season=4, episode=3, title="Tomorrow"),
            _episode(airdate=date(2026, 8, 21), season=4, episode=4, title="Third"),
        ),
        today,
    )

    assert 'class="calendar-page-heading"' in page
    assert "Calendario" in page
    assert "Oggi · 19 agosto" in page
    assert "Domani · 20 agosto" in page
    assert "Venerdì 21 agosto" in page
    assert page.count('class="calendar-day"') == 3
    assert "04x01" in page
    assert "04x02" in page
    assert "04x03" in page
    assert "04x04" in page
    assert "Premiere" in page
    assert "Second" in page
    assert "Tomorrow" in page
    assert "Third" in page


def test_calendar_renders_provider_logo_when_available() -> None:
    availability = SeasonAvailability(
        season_number=4,
        region="IT",
        providers=(
            AvailabilityProvider(
                "Disney Plus",
                AvailabilityType.STREAM,
                logo_url="https://img.example/disney-plus.png",
            ),
        ),
        source="JustWatch",
    )

    page = _render_calendar_page(
        (
            _episode(
                airdate=date(2026, 8, 19),
                season=4,
                episode=1,
                title="Premiere",
                availability=availability,
            ),
        ),
        date(2026, 8, 19),
    )

    assert 'class="calendar-provider-logo"' in page
    assert 'src="https://img.example/disney-plus.png"' in page
    assert 'alt="Disney Plus"' in page
    assert "Disney Plus" in page


def test_calendar_keeps_provider_name_when_logo_is_missing() -> None:
    availability = SeasonAvailability(
        season_number=4,
        region="IT",
        providers=(AvailabilityProvider("Apple TV Plus", AvailabilityType.STREAM),),
        source="JustWatch",
    )

    page = _render_calendar_page(
        (
            _episode(
                airdate=date(2026, 8, 19),
                season=4,
                episode=1,
                title="Premiere",
                availability=availability,
            ),
        ),
        date(2026, 8, 19),
    )

    assert "Apple TV Plus" in page
    assert 'class="calendar-provider-logo"' not in page


def test_calendar_renders_empty_state() -> None:
    page = _render_calendar_page((), date(2026, 8, 19))

    assert "Nessuna uscita in programma" in page
    assert "Le nuove puntate delle serie che segui appariranno qui." in page


def test_calendar_links_to_release_reminder_preferences_even_when_empty() -> None:
    page = _render_calendar_page((), date(2026, 8, 19))

    assert '<a class="section-link" href="/reminders">Gestisci promemoria</a>' in page


def test_mobile_navigation_links_to_dedicated_calendar() -> None:
    navigation = _render_mobile_nav()

    assert 'href="/calendar">Calendario</a>' in navigation
    assert 'href="/#upcoming">Calendario</a>' not in navigation
