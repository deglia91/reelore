"""Runtime orchestration for planning and delivering TV release reminders."""

from datetime import date
from typing import Protocol

from reelore.application.library_view import UpcomingEpisodeView
from reelore.application.release_reminders import ReleaseReminder, plan_release_reminders


class UpcomingReleaseReader(Protocol):
    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]: ...


class ReleaseReminderDelivery(Protocol):
    def deliver(self, reminders: tuple[ReleaseReminder, ...]) -> int: ...


class ReleaseReminderRuntime:
    """Plan due reminders from current upcoming releases and deliver them."""

    def __init__(
        self,
        upcoming_reader: UpcomingReleaseReader,
        delivery: ReleaseReminderDelivery,
    ) -> None:
        self._upcoming_reader = upcoming_reader
        self._delivery = delivery

    def run(self, today: date) -> int:
        reminders = plan_release_reminders(
            self._upcoming_reader.list_upcoming_episodes(today),
            today,
        )
        return self._delivery.deliver(reminders)
