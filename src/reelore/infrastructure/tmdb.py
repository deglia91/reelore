"""TMDB adapter for localized Italian TV metadata."""

import json
from collections.abc import Mapping
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from reelore.application import TVSeriesCatalog
from reelore.application.localization import (
    LocalizedEpisodeMetadata,
    LocalizedTVSeriesMetadata,
)


class TMDBLocalizerError(RuntimeError):
    """Raised when TMDB cannot provide valid localization metadata."""


class AuthorizedJsonHttpClient(Protocol):
    def get(self, url: str, token: str) -> object: ...


class UrllibAuthorizedJsonHttpClient:
    def __init__(self, *, timeout: float = 10.0) -> None:
        self._timeout = timeout

    def get(self, url: str, token: str) -> object:
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "User-Agent": "Reelore/0.1",
            },
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:
                payload: object = json.load(response)
        except (HTTPError, URLError, json.JSONDecodeError) as exc:
            raise TMDBLocalizerError(f"TMDB request failed: {exc}") from exc
        return payload


class TMDBItalianLocalizer:
    """Resolve a TVmaze catalog to Italian metadata from TMDB."""

    def __init__(
        self,
        token: str,
        client: AuthorizedJsonHttpClient | None = None,
        *,
        base_url: str = "https://api.themoviedb.org/3",
    ) -> None:
        if not token.strip():
            raise ValueError("TMDB API token cannot be empty")
        self._token = token
        self._client = client or UrllibAuthorizedJsonHttpClient()
        self._base_url = base_url.rstrip("/")

    def localize(self, catalog: TVSeriesCatalog) -> LocalizedTVSeriesMetadata | None:
        match = self._find_series(catalog)
        if match is None:
            return None
        tmdb_id = _required_int(match, "id")
        details = self._get(f"/tv/{tmdb_id}", {"language": "it-IT"})
        episodes = self._localized_episodes(tmdb_id, catalog)
        return LocalizedTVSeriesMetadata(
            title=_text_or_none(details.get("name")),
            summary=_text_or_none(details.get("overview")),
            episodes=episodes,
        )

    def _find_series(self, catalog: TVSeriesCatalog) -> Mapping[str, object] | None:
        payload = self._get(
            "/search/tv",
            {
                "query": catalog.title,
                "language": "it-IT",
                "include_adult": "false",
            },
        )
        results = _as_list(payload.get("results", []))
        if not results:
            return None
        candidates = [_as_mapping(item) for item in results]
        if catalog.premiered is not None:
            year = str(catalog.premiered.year)
            for candidate in candidates:
                first_air_date = _text_or_none(candidate.get("first_air_date"))
                if first_air_date and first_air_date.startswith(year):
                    return candidate
        return candidates[0]

    def _localized_episodes(
        self,
        tmdb_id: int,
        catalog: TVSeriesCatalog,
    ) -> tuple[LocalizedEpisodeMetadata, ...]:
        season_numbers = sorted({episode.season_number for episode in catalog.episodes})
        localized: list[LocalizedEpisodeMetadata] = []
        for season_number in season_numbers:
            season = self._get(
                f"/tv/{tmdb_id}/season/{season_number}",
                {"language": "it-IT"},
            )
            for item in _as_list(season.get("episodes", [])):
                episode = _as_mapping(item)
                number = _int_or_none(episode.get("episode_number"))
                if number is None or number < 1:
                    continue
                localized.append(
                    LocalizedEpisodeMetadata(
                        season_number=season_number,
                        episode_number=number,
                        title=_text_or_none(episode.get("name")),
                        summary=_text_or_none(episode.get("overview")),
                    )
                )
        return tuple(localized)

    def _get(self, path: str, params: Mapping[str, str]) -> Mapping[str, object]:
        encoded_path = quote(path, safe="/")
        url = f"{self._base_url}{encoded_path}?{urlencode(params)}"
        return _as_mapping(self._client.get(url, self._token))


def _as_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise TMDBLocalizerError("TMDB returned an invalid object")
    return cast(dict[str, object], value)


def _as_list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise TMDBLocalizerError("TMDB returned an invalid list")
    return cast(list[object], value)


def _required_int(row: Mapping[str, object], key: str) -> int:
    value = _int_or_none(row.get(key))
    if value is None:
        raise TMDBLocalizerError(f"TMDB response is missing {key}")
    return value


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TMDBLocalizerError("TMDB returned an invalid integer")
    return value


def _text_or_none(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TMDBLocalizerError("TMDB returned invalid text")
    return value or None
