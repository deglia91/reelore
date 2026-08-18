"""SQLite implementation of the authoritative personal media library."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import sqlite3

from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS media_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    media_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS personal_media_states (
    media_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    completion_count INTEGER NOT NULL CHECK (completion_count >= 0),
    FOREIGN KEY (media_id) REFERENCES media_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seen_episodes (
    media_id TEXT NOT NULL,
    season_number INTEGER NOT NULL CHECK (season_number > 0),
    episode_number INTEGER NOT NULL CHECK (episode_number > 0),
    PRIMARY KEY (media_id, season_number, episode_number),
    FOREIGN KEY (media_id) REFERENCES media_items(id) ON DELETE CASCADE
);
"""


class SQLiteLibraryRepository:
    """Persist media metadata and personal tracking state in SQLite."""

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

    def save_media(self, media: MediaItem) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO media_items (id, title, media_type)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    media_type = excluded.media_type
                """,
                (media.id, media.title, media.media_type.value),
            )

    def get_media(self, media_id: str) -> MediaItem | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT id, title, media_type FROM media_items WHERE id = ?",
                (media_id,),
            ).fetchone()

        if row is None:
            return None
        return MediaItem(id=str(row[0]), title=str(row[1]), media_type=MediaType(str(row[2])))

    def save_personal_state(self, state: PersonalMediaState) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO personal_media_states (media_id, status, completion_count)
                VALUES (?, ?, ?)
                ON CONFLICT(media_id) DO UPDATE SET
                    status = excluded.status,
                    completion_count = excluded.completion_count
                """,
                (state.media_id, state.status.value, state.completion_count),
            )

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT media_id, status, completion_count
                FROM personal_media_states
                WHERE media_id = ?
                """,
                (media_id,),
            ).fetchone()

        if row is None:
            return None
        return PersonalMediaState(
            media_id=str(row[0]),
            status=LibraryStatus(str(row[1])),
            completion_count=int(row[2]),
        )

    def save_episode_progress(self, progress: EpisodeProgress) -> None:
        rows = [
            (progress.media_id, episode.season_number, episode.episode_number)
            for episode in sorted(progress.seen_episodes)
        ]
        with self._connection() as connection:
            connection.execute(
                "DELETE FROM seen_episodes WHERE media_id = ?",
                (progress.media_id,),
            )
            connection.executemany(
                """
                INSERT INTO seen_episodes (media_id, season_number, episode_number)
                VALUES (?, ?, ?)
                """,
                rows,
            )

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT season_number, episode_number
                FROM seen_episodes
                WHERE media_id = ?
                ORDER BY season_number, episode_number
                """,
                (media_id,),
            ).fetchall()

        episodes = frozenset(
            EpisodeRef(season_number=int(row[0]), episode_number=int(row[1])) for row in rows
        )
        return EpisodeProgress(media_id=media_id, seen_episodes=episodes)
