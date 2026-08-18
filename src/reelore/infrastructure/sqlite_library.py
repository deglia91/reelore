"""SQLite implementation of Reelore's authoritative local data store."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from reelore.application import TVCastMember, TVEpisodeMetadata, TVSeriesCatalog
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

CREATE TABLE IF NOT EXISTS tv_series_catalog (
    provider_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    status TEXT,
    premiered TEXT,
    ended TEXT,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS tv_episode_catalog (
    series_provider_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    season_number INTEGER NOT NULL CHECK (season_number > 0),
    episode_number INTEGER NOT NULL CHECK (episode_number > 0),
    title TEXT NOT NULL,
    airdate TEXT,
    summary TEXT,
    image_url TEXT,
    PRIMARY KEY (series_provider_id, provider_id),
    FOREIGN KEY (series_provider_id) REFERENCES tv_series_catalog(provider_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tv_cast_catalog (
    series_provider_id TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position >= 0),
    person_name TEXT NOT NULL,
    character_name TEXT NOT NULL,
    image_url TEXT,
    PRIMARY KEY (series_provider_id, position),
    FOREIGN KEY (series_provider_id) REFERENCES tv_series_catalog(provider_id) ON DELETE CASCADE
);
"""


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _date_from_text(value: object) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(str(value))


class SQLiteLibraryRepository:
    """Persist personal tracking state and cached provider-neutral catalog metadata."""

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

    def save_tv_series_catalog(self, catalog: TVSeriesCatalog) -> None:
        episode_rows = [
            (
                catalog.provider_id,
                episode.provider_id,
                episode.season_number,
                episode.episode_number,
                episode.title,
                _date_to_text(episode.airdate),
                episode.summary,
                episode.image_url,
            )
            for episode in catalog.episodes
        ]
        cast_rows = [
            (
                catalog.provider_id,
                position,
                member.person_name,
                member.character_name,
                member.image_url,
            )
            for position, member in enumerate(catalog.cast)
        ]
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO tv_series_catalog
                    (provider_id, title, summary, status, premiered, ended, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider_id) DO UPDATE SET
                    title = excluded.title,
                    summary = excluded.summary,
                    status = excluded.status,
                    premiered = excluded.premiered,
                    ended = excluded.ended,
                    image_url = excluded.image_url
                """,
                (
                    catalog.provider_id,
                    catalog.title,
                    catalog.summary,
                    catalog.status,
                    _date_to_text(catalog.premiered),
                    _date_to_text(catalog.ended),
                    catalog.image_url,
                ),
            )
            connection.execute(
                "DELETE FROM tv_episode_catalog WHERE series_provider_id = ?",
                (catalog.provider_id,),
            )
            connection.execute(
                "DELETE FROM tv_cast_catalog WHERE series_provider_id = ?",
                (catalog.provider_id,),
            )
            connection.executemany(
                """
                INSERT INTO tv_episode_catalog
                    (series_provider_id, provider_id, season_number, episode_number,
                     title, airdate, summary, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                episode_rows,
            )
            connection.executemany(
                """
                INSERT INTO tv_cast_catalog
                    (series_provider_id, position, person_name, character_name, image_url)
                VALUES (?, ?, ?, ?, ?)
                """,
                cast_rows,
            )

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        with self._connection() as connection:
            series_row = connection.execute(
                """
                SELECT provider_id, title, summary, status, premiered, ended, image_url
                FROM tv_series_catalog
                WHERE provider_id = ?
                """,
                (provider_id,),
            ).fetchone()
            if series_row is None:
                return None
            episode_rows = connection.execute(
                """
                SELECT provider_id, season_number, episode_number, title, airdate, summary, image_url
                FROM tv_episode_catalog
                WHERE series_provider_id = ?
                ORDER BY season_number, episode_number
                """,
                (provider_id,),
            ).fetchall()
            cast_rows = connection.execute(
                """
                SELECT person_name, character_name, image_url
                FROM tv_cast_catalog
                WHERE series_provider_id = ?
                ORDER BY position
                """,
                (provider_id,),
            ).fetchall()

        episodes = tuple(
            TVEpisodeMetadata(
                provider_id=str(row[0]),
                season_number=int(row[1]),
                episode_number=int(row[2]),
                title=str(row[3]),
                airdate=_date_from_text(row[4]),
                summary=str(row[5]) if row[5] is not None else None,
                image_url=str(row[6]) if row[6] is not None else None,
            )
            for row in episode_rows
        )
        cast = tuple(
            TVCastMember(
                person_name=str(row[0]),
                character_name=str(row[1]),
                image_url=str(row[2]) if row[2] is not None else None,
            )
            for row in cast_rows
        )
        return TVSeriesCatalog(
            provider_id=str(series_row[0]),
            title=str(series_row[1]),
            summary=str(series_row[2]) if series_row[2] is not None else None,
            status=str(series_row[3]) if series_row[3] is not None else None,
            premiered=_date_from_text(series_row[4]),
            ended=_date_from_text(series_row[5]),
            image_url=str(series_row[6]) if series_row[6] is not None else None,
            episodes=episodes,
            cast=cast,
        )
