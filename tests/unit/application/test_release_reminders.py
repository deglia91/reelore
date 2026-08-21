from datetime import date

from reelore.application.library_view import UpcomingEpisodeView
from reelore.application.release_reminders import (
    ReleaseReminder,
    ReleaseReminderDeliveryService,
    ReleaseReminderKind,
    plan_release_reminders,
)


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


def _reminder(kind: ReleaseReminderKind = ReleaseReminderKind.TODAY) -> ReleaseReminder:
    return ReleaseReminder(
        media_id="tvmaze:1",
        series_title="Example",
        season_number=2,
        episode_number=1,
        episode_title="Episode 1",
        airdate=date(2026, 8, 21),
        kind=kind,
    )


class StubReminderHistory:
    def __init__(self) -> None:
        self.delivered: set[tuple[str, int, int, ReleaseReminderKind]] = set()

    def was_delivered(self, reminder: ReleaseReminder) -> bool:
        return self._key(reminder) in self.delivered

    def record_delivered(self, reminder: ReleaseReminder) -> None:
        self.delivered.add(self._key(reminder))

    @staticmethod
    def _key(reminder: ReleaseReminder) -> tuple[str, int, int, ReleaseReminderKind]:
        return (
            reminder.media_id,
            reminder.season_number,
            reminder.episode_number,
            reminder.kind,
        )


class StubNotifier:
    def __init__(self) -> None:
        self.sent: list[ReleaseReminder] = []

    def notify(self, reminder: ReleaseReminder) -> None:
        self.sent.append(reminder)


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


def test_delivery_service_sends_each_reminder_kind_only_once() -> None:
    history = StubReminderHistory()
    notifier = StubNotifier()
    service = ReleaseReminderDeliveryService(history, notifier)
    today = _reminder()
    tomorrow = _reminder(ReleaseReminderKind.TOMORROW)

    assert service.deliver((today, tomorrow)) == 2
    assert service.deliver((today, tomorrow)) == 0

    assert notifier.sent == [today, tomorrow]


def test_delivery_service_records_only_successful_notifications() -> None:
    history = StubReminderHistory()

    class FailingNotifier:
        def notify(self, reminder: ReleaseReminder) -> None:
            raise RuntimeError("notification failed")

    service = ReleaseReminderDeliveryService(history, FailingNotifier())
    reminder = _reminder()

    try:
        service.deliver((reminder,))
    except RuntimeError:
        pass

    assert history.was_delivered(reminder) is False
