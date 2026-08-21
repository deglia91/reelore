from datetime import date

from reelore.application.library_view import UpcomingEpisodeView
from reelore.application.release_reminders import ReleaseReminder
from reelore.release_reminder_runtime import ReleaseReminderRuntime


class StubUpcomingReader:
    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]:
        return (
            UpcomingEpisodeView(
                media_id="tvmaze:1",
                series_title="Example",
                season_number=2,
                episode_number=1,
                episode_title="Today",
                airdate=today,
                image_url=None,
            ),
            UpcomingEpisodeView(
                media_id="tvmaze:1",
                series_title="Example",
                season_number=2,
                episode_number=2,
                episode_title="Later",
                airdate=date(2026, 8, 30),
                image_url=None,
            ),
        )


class StubDelivery:
    def __init__(self) -> None:
        self.received: tuple[ReleaseReminder, ...] = ()

    def deliver(self, reminders: tuple[ReleaseReminder, ...]) -> int:
        self.received = reminders
        return len(reminders)


def test_release_reminder_runtime_plans_due_releases_before_delivery() -> None:
    delivery = StubDelivery()
    runtime = ReleaseReminderRuntime(StubUpcomingReader(), delivery)

    delivered = runtime.run(date(2026, 8, 21))

    assert delivered == 1
    assert len(delivery.received) == 1
    assert delivery.received[0].episode_title == "Today"
