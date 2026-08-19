"""SQLite adapter for append-only episode watch history."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from reelore.domain import EpisodeRef, EpisodeWatch

_SCHEMA = """
CREATE TABLE IF NOT EXISTS episode_watches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id TEXT NOT NULL,
    season_number INTEGER NOT NULL CHECK (season_number > 0),
    episode_number INTEGER NOT NULL CHECK (episode_number > 0),
    watched_at TEXT,
    FOREIGN KEY (media_id) REFERENCES media_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_episode_watches_media_episode
ON episode_watches (media_id, season_number, episode_number, id);

CREATE TABLE IF NOT EXISTS episode_watch_retractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    watch_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (watch_id) REFERENCES episode_watches(id) ON DELETE CASCADE
);
"""


def _datetime_to_text(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _datetime_from_text(value: object) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(str(value))


class SQLiteWatchHistoryRepository:
    """Persist episode watch records while preserving legacy seen progress."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = str(database_path)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
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
            connection.execute(
                """
                INSERT INTO episode_watches
                    (media_id, season_number, episode_number, watched_at)
                SELECT
                    legacy.media_id,
                    legacy.season_number,
                    legacy.episode_number,
                    NULL
                FROM seen_episodes AS legacy
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM episode_watches AS history
                    WHERE history.media_id = legacy.media_id
                      AND history.season_number = legacy.season_number
                      AND history.episode_number = legacy.episode_number
                )
                """
            )

    def record_episode_watch(self, watch: EpisodeWatch) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO episode_watches
                    (media_id, season_number, episode_number, watched_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    watch.media_id,
                    watch.episode.season_number,
                    watch.episode.episode_number,
                    _datetime_to_text(watch.watched_at),
                ),
            )

    def list_episode_watches(self, media_id: str) -> tuple[EpisodeWatch, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT history.season_number, history.episode_number, history.watched_at
                FROM episode_watches AS history
                LEFT JOIN episode_watch_retractions AS retraction
                  ON retraction.watch_id = history.id
                WHERE history.media_id = ?
                  AND retraction.watch_id IS NULL
                ORDER BY history.id
                """,
                (media_id,),
            ).fetchall()

        return tuple(
            EpisodeWatch(
                media_id=media_id,
                episode=EpisodeRef(
                    season_number=int(row[0]),
                    episode_number=int(row[1]),
                ),
                watched_at=_datetime_from_text(row[2]),
            )
            for row in rows
        )

    def retract_latest_episode_watch(self, media_id: str, episode: EpisodeRef) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT history.id
                FROM episode_watches AS history
                LEFT JOIN episode_watch_retractions AS retraction
                  ON retraction.watch_id = history.id
                WHERE history.media_id = ?
                  AND history.season_number = ?
                  AND history.episode_number = ?
                  AND retraction.watch_id IS NULL
                ORDER BY history.id DESC
                LIMIT 1
                """,
                (media_id, episode.season_number, episode.episode_number),
            ).fetchone()
            if row is None:
                return False
            connection.execute(
                "INSERT INTO episode_watch_retractions (watch_id) VALUES (?)",
                (int(row[0]),),
            )
            return True
