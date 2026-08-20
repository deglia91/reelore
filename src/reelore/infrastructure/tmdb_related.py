"""TMDB adapter for provider-ranked related TV titles."""

from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.related import RelatedTVTitle
from reelore.infrastructure.tmdb import (
    AuthorizedJsonHttpClient,
    TMDBAdapter,
    as_list,
    as_mapping,
    int_or_none,
    text_or_none,
)

_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w342"


class TMDBRelatedTVProvider(TMDBAdapter):
    """Resolve a source series and return TMDB TV recommendations in Italian."""

    def __init__(
        self,
        token: str,
        client: AuthorizedJsonHttpClient | None = None,
        *,
        base_url: str = "https://api.themoviedb.org/3",
    ) -> None:
        super().__init__(token, client, base_url)

    def related_to(self, catalog: TVSeriesCatalog) -> tuple[RelatedTVTitle, ...]:
        match = self._find_series(catalog)
        if match is None:
            return ()
        tmdb_id = int_or_none(match.get("id"))
        if tmdb_id is None:
            return ()
        payload = self._get(
            f"/tv/{tmdb_id}/recommendations",
            {"language": "it-IT", "page": "1"},
        )
        related: list[RelatedTVTitle] = []
        for item in as_list(payload.get("results", [])):
            row = as_mapping(item)
            provider_id = int_or_none(row.get("id"))
            title = text_or_none(row.get("name"))
            if provider_id is None or title is None:
                continue
            related.append(
                RelatedTVTitle(
                    provider_key=str(provider_id),
                    title=title,
                    premiered=_date_or_none(row.get("first_air_date")),
                    summary=text_or_none(row.get("overview")),
                    image_url=_poster_url(row.get("poster_path")),
                )
            )
        return tuple(related)


def _date_or_none(value: object) -> date | None:
    text = text_or_none(value)
    if text is None:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _poster_url(value: object) -> str | None:
    path = text_or_none(value)
    if path is None:
        return None
    return f"{_IMAGE_BASE_URL}{path}"
