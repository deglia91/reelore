from datetime import date
from pathlib import Path

from reelore.application.release_reminders import ReleaseReminder, ReleaseReminderKind
from reelore.infrastructure.sqlite_release_reminders import SQLiteReleaseReminderHistory


def _reminder(kind: ReleaseReminderKind = ReleaseReminderKind.TODAY) -> ReleaseReminder:
    return ReleaseReminder(
        media_id="tvmaze:1",
        series_title="Example",
        season_number=2,
        episode_number=3,
        episode_title="Episode 3",
        airdate=date(2026, 8, 21),
        kind=kind,
    )


def test_sqlite_release_reminder_history_persists_delivery(tmp_path: Path) -> None:
    database_path = tmp_path / "reelore.db"
    history = SQLiteReleaseReminderHistory(database_path)
    history.initialize()
    reminder = _reminder()

    assert history.was_delivered(reminder) is False

    history.record_delivered(reminder)

    reopened = SQLiteReleaseReminderHistory(database_path)
    reopened.initialize()
    assert reopened.was_delivered(reminder) is True


def test_sqlite_release_reminder_history_distinguishes_reminder_kind(tmp_path: Path) -> None:
    history = SQLiteReleaseReminderHistory(tmp_path / "reelore.db")
    history.initialize()
    history.record_delivered(_reminder(ReleaseReminderKind.TOMORROW))

    assert history.was_delivered(_reminder(ReleaseReminderKind.TOMORROW)) is True
    assert history.was_delivered(_reminder(ReleaseReminderKind.TODAY)) is False


def test_sqlite_release_reminder_history_record_is_idempotent(tmp_path: Path) -> None:
    history = SQLiteReleaseReminderHistory(tmp_path / "reelore.db")
    history.initialize()
    reminder = _reminder()

    history.record_delivered(reminder)
    history.record_delivered(reminder)

    assert history.was_delivered(reminder) is True
