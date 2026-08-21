from pathlib import Path

from reelore.application.release_reminders import ReleaseReminderPreferences
from reelore.infrastructure.sqlite_release_reminder_preferences import (
    SQLiteReleaseReminderPreferences,
)


def test_release_reminder_preferences_default_to_today_and_tomorrow(tmp_path: Path) -> None:
    store = SQLiteReleaseReminderPreferences(tmp_path / "reelore.db")
    store.initialize()

    assert store.get_preferences() == ReleaseReminderPreferences()


def test_release_reminder_preferences_persist_across_restarts(tmp_path: Path) -> None:
    database_path = tmp_path / "reelore.db"
    store = SQLiteReleaseReminderPreferences(database_path)
    store.initialize()
    store.save_preferences(
        ReleaseReminderPreferences(today_enabled=True, tomorrow_enabled=False)
    )

    reopened = SQLiteReleaseReminderPreferences(database_path)
    reopened.initialize()

    assert reopened.get_preferences() == ReleaseReminderPreferences(
        today_enabled=True,
        tomorrow_enabled=False,
    )
