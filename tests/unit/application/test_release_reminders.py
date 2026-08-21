from datetime import date

from reelore.application.library_view import UpcomingEpisodeView
from reelore.application.release_reminders import ReleaseReminderKind, plan_release_reminders


def _episode(*, airdate: date, episode: int) -> UpcomingEpisodeView:
    return UpcomingEpisodeView(
        media_id="tvmaze:1",
        series_title="Example",
        season_number=2,
        episode_number=episode,
        episode_title=f"Episode {episode}",
        airdate=airdate,
        image_url=None,
    )


def test_release_reminders_include_today_and_tomorrow_only() -> None:
    today = date(2026, 8, 21)

    reminders = plan_release_reminders(
        (
            _episode(airdate=today, episode=1),
            _episode(airdate=date(2026, 8, 22), episode=2),
            _episode(airdate=date(2026, 8, 23), episode=3),
        ),
        today,
    )

    assert [(item.episode_number, item.kind) for item in reminders] == [
        (1, ReleaseReminderKind.TODAY),
        (2, ReleaseReminderKind.TOMORROW),
    ]
    assert reminders[0].series_title == "Example"
    assert reminders[0].season_number == 2
    assert reminders[0].episode_title == "Episode 1"
