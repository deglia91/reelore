"""TVmaze adapter for provider-independent TV catalog metadata."""

import json
from collections.abc import Mapping
from datetime import date
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from reelore.application import (
    TVCastMember,
    TVEpisodeMetadata,
    TVSearchResult,
    TVSeriesCatalog,
)


class TVMazeProviderError(RuntimeError):
    """Raised when TVmaze cannot provide a valid response."""


class JsonHttpClient(Protocol):
    def get(self, url: str) -> object: ...


class UrllibJsonHttpClient:
    def __init__(self, *, timeout: float = 10.0) -> None:
        self._timeout = timeout

    def get(self, url: str) -> object:
        request = Request(url, headers={"User-Agent": "Reelore/0.1"})
        try:
            with urlopen(request, timeout=self._timeout) as response:
                payload: object = json.load(response)
        except (HTTPError, URLError, json.JSONDecodeError) as exc:
            raise TVMazeProviderError(f"TVmaze request failed: {exc}") from exc
        return payload


class TVMazeProvider:
    """Retrieve TV series metadata from TVmaze's public API."""

    def __init__(
        self,
        client: JsonHttpClient | None = None,
        *,
        base_url: str = "https://api.tvmaze.com",
    ) -> None:
        self._client = client or UrllibJsonHttpClient()
        self._base_url = base_url.rstrip("/")

    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("search query cannot be empty")

        url = f"{self._base_url}/search/shows?{urlencode({'q': normalized_query})}"
        payload = _as_list(self._client.get(url))
        results: list[TVSearchResult] = []
        for item in payload:
            row = _as_mapping(item)
            show = _as_mapping(row.get("show"))
            results.append(
                TVSearchResult(
                    provider_id=str(_required_int(show, "id")),
                    title=_required_text(show, "name"),
                    premiered=_date_or_none(show.get("premiered")),
                    status=_text_or_none(show.get("status")),
                    image_url=_image_url(show.get("image")),
                )
            )
        return tuple(results)

    def get_series(self, provider_id: str) -> TVSeriesCatalog:
        normalized_id = provider_id.strip()
        if not normalized_id:
            raise ValueError("provider id cannot be empty")

        encoded_id = quote(normalized_id, safe="")
        embeds = urlencode([("embed[]", "episodes"), ("embed[]", "cast")])
        url = f"{self._base_url}/shows/{encoded_id}?{embeds}"
        show = _as_mapping(self._client.get(url))
        embedded = _as_mapping(show.get("_embedded"))

        episodes = tuple(
            episode
            for item in _as_list(embedded.get("episodes", []))
            if (episode := _episode_or_none(item)) is not None
        )
        cast_members = tuple(_cast_member(item) for item in _as_list(embedded.get("cast", [])))

        return TVSeriesCatalog(
            provider_id=str(_required_int(show, "id")),
            title=_required_text(show, "name"),
            summary=_text_or_none(show.get("summary")),
            status=_text_or_none(show.get("status")),
            premiered=_date_or_none(show.get("premiered")),
            ended=_date_or_none(show.get("ended")),
            image_url=_image_url(show.get("image")),
            episodes=episodes,
            cast=cast_members,
        )


def _episode_or_none(value: object) -> TVEpisodeMetadata | None:
    row = _as_mapping(value)
    season = _int_or_none(row.get("season"))
    number = _int_or_none(row.get("number"))
    if season is None or number is None or season < 1 or number < 1:
        return None
    return TVEpisodeMetadata(
        provider_id=str(_required_int(row, "id")),
        season_number=season,
        episode_number=number,
        title=_required_text(row, "name"),
        airdate=_date_or_none(row.get("airdate")),
        summary=_text_or_none(row.get("summary")),
        image_url=_image_url(row.get("image")),
        runtime_minutes=_int_or_none(row.get("runtime")),
    )


def _cast_member(value: object) -> TVCastMember:
    row = _as_mapping(value)
    person = _as_mapping(row.get("person"))
    character = _as_mapping(row.get("character"))
    return TVCastMember(
        person_name=_required_text(person, "name"),
        character_name=_required_text(character, "name"),
        image_url=_image_url(person.get("image")),
    )


def _as_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise TVMazeProviderError("TVmaze returned an invalid object")
    return cast(dict[str, object], value)


def _as_list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise TVMazeProviderError("TVmaze returned an invalid list")
    return cast(list[object], value)


def _required_text(row: Mapping[str, object], key: str) -> str:
    value = _text_or_none(row.get(key))
    if value is None:
        raise TVMazeProviderError(f"TVmaze response is missing {key}")
    return value


def _required_int(row: Mapping[str, object], key: str) -> int:
    value = _int_or_none(row.get(key))
    if value is None:
        raise TVMazeProviderError(f"TVmaze response is missing {key}")
    return value


def _text_or_none(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TVMazeProviderError("TVmaze returned invalid text")
    return value


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TVMazeProviderError("TVmaze returned an invalid integer")
    return value


def _date_or_none(value: object) -> date | None:
    text = _text_or_none(value)
    if text is None or not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise TVMazeProviderError("TVmaze returned an invalid date") from exc


def _image_url(value: object) -> str | None:
    if value is None:
        return None
    image = _as_mapping(value)
    return _text_or_none(image.get("original")) or _text_or_none(image.get("medium"))
