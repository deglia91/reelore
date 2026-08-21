"""Periodic scheduler for release reminders while NextEp remains running."""

from collections.abc import Callable
from datetime import date
from threading import Event, Thread
from typing import Protocol


class ScheduledReminderRuntime(Protocol):
    def run(self, today: date) -> int: ...


def start_release_reminder_scheduler(
    runtime: ScheduledReminderRuntime,
    *,
    interval_seconds: float = 3600,
    stop_event: Event | None = None,
    today_provider: Callable[[], date] = date.today,
) -> Thread:
    """Run reminder checks periodically in a daemon thread after the startup check."""

    stop = stop_event or Event()

    def run_periodically() -> None:
        while not stop.wait(interval_seconds):
            runtime.run(today_provider())

    thread = Thread(
        target=run_periodically,
        name="reelore-release-reminders",
        daemon=True,
    )
    thread.start()
    return thread
