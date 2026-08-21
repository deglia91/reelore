"""Runtime orchestration for planning and delivering TV release reminders."""

from datetime import date
from typing import Protocol

from reelore.application.library_view import UpcomingEpisodeView
from reelore.application.release_reminders import (
    ReleaseReminder,
    ReleaseReminderPreferences,
    plan_release_reminders,
)


class UpcomingReleaseReader(Protocol):
    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]: ...


class ReleaseReminderDelivery(Protocol):
    def deliver(self, reminders: tuple[ReleaseReminder, ...]) -> int: ...


class ReleaseReminderPreferencesReader(Protocol):
    def get_preferences(self) -> ReleaseReminderPreferences: ...


class ReleaseReminderRuntime:
    """Plan due reminders from current upcoming releases and deliver them."""

    def __init__(
        self,
        upcoming_reader: UpcomingReleaseReader,
        delivery: ReleaseReminderDelivery,
        preferences: ReleaseReminderPreferencesReader | None = None,
    ) -> None:
        self._upcoming_reader = upcoming_reader
        self._delivery = delivery
        self._preferences = preferences

    def run(self, today: date) -> int:
        reminders = plan_release_reminders(
            self._upcoming_reader.list_upcoming_episodes(today),
            today,
        )
        preferences = (
            self._preferences.get_preferences()
            if self._preferences is not None
            else ReleaseReminderPreferences()
        )
        enabled = tuple(reminder for reminder in reminders if preferences.allows(reminder.kind))
        return self._delivery.deliver(enabled)
