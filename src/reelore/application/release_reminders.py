"""Plan and deliver release reminders for upcoming TV episodes."""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Protocol

from reelore.application.library_view import UpcomingEpisodeView


class ReleaseReminderKind(StrEnum):
    TODAY = "today"
    TOMORROW = "tomorrow"


@dataclass(frozen=True, slots=True)
class ReleaseReminder:
    media_id: str
    series_title: str
    season_number: int
    episode_number: int
    episode_title: str
    airdate: date
    kind: ReleaseReminderKind


class ReleaseReminderHistory(Protocol):
    def was_delivered(self, reminder: ReleaseReminder) -> bool: ...

    def record_delivered(self, reminder: ReleaseReminder) -> None: ...


class ReleaseReminderNotifier(Protocol):
    def notify(self, reminder: ReleaseReminder) -> None: ...


class ReleaseReminderDeliveryService:
    """Deliver due reminders once per episode and reminder kind."""

    def __init__(
        self,
        history: ReleaseReminderHistory,
        notifier: ReleaseReminderNotifier,
    ) -> None:
        self._history = history
        self._notifier = notifier

    def deliver(self, reminders: tuple[ReleaseReminder, ...]) -> int:
        delivered = 0
        for reminder in reminders:
            if self._history.was_delivered(reminder):
                continue
            self._notifier.notify(reminder)
            self._history.record_delivered(reminder)
            delivered += 1
        return delivered


def plan_release_reminders(
    episodes: tuple[UpcomingEpisodeView, ...],
    today: date,
) -> tuple[ReleaseReminder, ...]:
    tomorrow = today + timedelta(days=1)
    reminders: list[ReleaseReminder] = []
    for episode in episodes:
        if episode.airdate == today:
            kind = ReleaseReminderKind.TODAY
        elif episode.airdate == tomorrow:
            kind = ReleaseReminderKind.TOMORROW
        else:
            continue
        reminders.append(
            ReleaseReminder(
                media_id=episode.media_id,
                series_title=episode.series_title,
                season_number=episode.season_number,
                episode_number=episode.episode_number,
                episode_title=episode.episode_title,
                airdate=episode.airdate,
                kind=kind,
            )
        )
    return tuple(reminders)
