"""SQLite persistence for release reminder preferences."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from reelore.application.release_reminders import ReleaseReminderPreferences

_SCHEMA = """
CREATE TABLE IF NOT EXISTS release_reminder_preferences (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    today_enabled INTEGER NOT NULL CHECK (today_enabled IN (0, 1)),
    tomorrow_enabled INTEGER NOT NULL CHECK (tomorrow_enabled IN (0, 1))
);
"""


class SQLiteReleaseReminderPreferences:
    """Persist the single local user's reminder preferences."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = str(database_path)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(_SCHEMA)

    def get_preferences(self) -> ReleaseReminderPreferences:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT today_enabled, tomorrow_enabled
                FROM release_reminder_preferences
                WHERE id = 1
                """
            ).fetchone()
        if row is None:
            return ReleaseReminderPreferences()
        return ReleaseReminderPreferences(
            today_enabled=bool(row[0]),
            tomorrow_enabled=bool(row[1]),
        )

    def save_preferences(self, preferences: ReleaseReminderPreferences) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO release_reminder_preferences
                    (id, today_enabled, tomorrow_enabled)
                VALUES (1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    today_enabled = excluded.today_enabled,
                    tomorrow_enabled = excluded.tomorrow_enabled
                """,
                (int(preferences.today_enabled), int(preferences.tomorrow_enabled)),
            )
