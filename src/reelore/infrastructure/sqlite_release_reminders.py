"""SQLite persistence for delivered TV release reminders."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from reelore.application.release_reminders import ReleaseReminder

_SCHEMA = """
CREATE TABLE IF NOT EXISTS release_reminder_deliveries (
    media_id TEXT NOT NULL,
    season_number INTEGER NOT NULL CHECK (season_number > 0),
    episode_number INTEGER NOT NULL CHECK (episode_number > 0),
    airdate TEXT NOT NULL,
    reminder_kind TEXT NOT NULL,
    PRIMARY KEY (media_id, season_number, episode_number, airdate, reminder_kind)
);
"""


class SQLiteReleaseReminderHistory:
    """Remember delivered reminders across application restarts."""

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

    def was_delivered(self, reminder: ReleaseReminder) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM release_reminder_deliveries
                WHERE media_id = ?
                  AND season_number = ?
                  AND episode_number = ?
                  AND airdate = ?
                  AND reminder_kind = ?
                LIMIT 1
                """,
                (
                    reminder.media_id,
                    reminder.season_number,
                    reminder.episode_number,
                    reminder.airdate.isoformat(),
                    reminder.kind.value,
                ),
            ).fetchone()
        return row is not None

    def record_delivered(self, reminder: ReleaseReminder) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO release_reminder_deliveries
                    (media_id, season_number, episode_number, airdate, reminder_kind)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    reminder.media_id,
                    reminder.season_number,
                    reminder.episode_number,
                    reminder.airdate.isoformat(),
                    reminder.kind.value,
                ),
            )
