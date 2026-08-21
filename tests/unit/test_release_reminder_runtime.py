from datetime import date, timedelta

from reelore.application.library_view import UpcomingEpisodeView
from reelore.application.release_reminders import ReleaseReminder, ReleaseReminderPreferences
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
                episode_title="Tomorrow",
                airdate=today + timedelta(days=1),
                image_url=None,
            ),
            UpcomingEpisodeView(
                media_id="tvmaze:1",
                series_title="Example",
                season_number=2,
                episode_number=3,
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


class StubPreferences:
    def __init__(self, preferences: ReleaseReminderPreferences) -> None:
        self.preferences = preferences

    def get_preferences(self) -> ReleaseReminderPreferences:
        return self.preferences


def test_release_reminder_runtime_plans_due_releases_before_delivery() -> None:
    delivery = StubDelivery()
    runtime = ReleaseReminderRuntime(StubUpcomingReader(), delivery)

    delivered = runtime.run(date(2026, 8, 21))

    assert delivered == 2
    assert [item.episode_title for item in delivery.received] == ["Today", "Tomorrow"]


def test_release_reminder_runtime_filters_disabled_reminder_kinds() -> None:
    delivery = StubDelivery()
    preferences = StubPreferences(
        ReleaseReminderPreferences(today_enabled=True, tomorrow_enabled=False)
    )
    runtime = ReleaseReminderRuntime(StubUpcomingReader(), delivery, preferences)

    delivered = runtime.run(date(2026, 8, 21))

    assert delivered == 1
    assert [item.episode_title for item in delivery.received] == ["Today"]
