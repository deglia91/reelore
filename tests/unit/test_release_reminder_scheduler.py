from datetime import date
from threading import Event

from reelore.release_reminder_scheduler import start_release_reminder_scheduler


class StubRuntime:
    def __init__(self, called: Event) -> None:
        self.called = called
        self.days: list[date] = []

    def run(self, today: date) -> int:
        self.days.append(today)
        self.called.set()
        return 1


def test_release_reminder_scheduler_runs_periodically_in_daemon_thread() -> None:
    called = Event()
    stop = Event()
    runtime = StubRuntime(called)

    thread = start_release_reminder_scheduler(
        runtime,
        interval_seconds=0.01,
        stop_event=stop,
        today_provider=lambda: date(2026, 8, 21),
    )

    assert thread.daemon is True
    assert thread.name == "reelore-release-reminders"
    assert called.wait(timeout=1)
    stop.set()
    thread.join(timeout=1)
    assert runtime.days[0] == date(2026, 8, 21)
