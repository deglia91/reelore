"""TMDB adapter for regional TV season availability."""

from collections.abc import Mapping
from typing import ClassVar

from reelore.application.availability import (
    AvailabilityProvider,
    AvailabilityType,
    SeasonAvailability,
)
from reelore.application.catalog import TVSeriesCatalog
from reelore.infrastructure.tmdb import (
    AuthorizedJsonHttpClient,
    TMDBAdapter,
    as_list,
    as_mapping,
    required_int,
    text_or_none,
)


class TMDBItalianAvailabilityProvider(TMDBAdapter):
    """Resolve Italian availability supplied by TMDB/JustWatch."""

    _PROVIDER_GROUPS: ClassVar[tuple[tuple[str, AvailabilityType], ...]] = (
        ("flatrate", AvailabilityType.STREAM),
        ("free", AvailabilityType.FREE),
        ("ads", AvailabilityType.ADS),
        ("rent", AvailabilityType.RENT),
        ("buy", AvailabilityType.BUY),
    )

    def __init__(
        self,
        token: str,
        client: AuthorizedJsonHttpClient | None = None,
        *,
        base_url: str = "https://api.themoviedb.org/3",
        image_base_url: str = "https://image.tmdb.org/t/p/w92",
    ) -> None:
        super().__init__(token, client, base_url)
        self._image_base_url = image_base_url.rstrip("/")

    def season_availability(
        self,
        catalog: TVSeriesCatalog,
        season_number: int,
        region: str = "IT",
    ) -> SeasonAvailability | None:
        match = self._find_series(catalog)
        if match is None:
            return None
        tmdb_id = required_int(match, "id")
        region_code = region.upper()
        season_payload = self._get(f"/tv/{tmdb_id}/season/{season_number}/watch/providers")
        region_payload = self._region_payload(season_payload, region_code)
        providers = self._providers(region_payload) if region_payload is not None else ()

        if not providers:
            series_payload = self._get(f"/tv/{tmdb_id}/watch/providers")
            region_payload = self._region_payload(series_payload, region_code)
            if region_payload is None:
                return None
            providers = self._providers(region_payload)

        if not providers or region_payload is None:
            return None
        return SeasonAvailability(
            season_number=season_number,
            region=region_code,
            providers=providers,
            source="JustWatch",
            source_url=text_or_none(region_payload.get("link")),
        )

    def _region_payload(
        self,
        payload: Mapping[str, object],
        region: str,
    ) -> Mapping[str, object] | None:
        regions = as_mapping(payload.get("results", {}))
        region_payload = regions.get(region)
        if region_payload is None:
            return None
        return as_mapping(region_payload)

    def _providers(
        self,
        region_payload: Mapping[str, object],
    ) -> tuple[AvailabilityProvider, ...]:
        providers: list[AvailabilityProvider] = []
        for group, availability_type in self._PROVIDER_GROUPS:
            for raw_provider in as_list(region_payload.get(group, [])):
                provider = as_mapping(raw_provider)
                name = text_or_none(provider.get("provider_name"))
                if name is None:
                    continue
                logo_path = text_or_none(provider.get("logo_path"))
                providers.append(
                    AvailabilityProvider(
                        name=name,
                        availability_type=availability_type,
                        logo_url=(
                            f"{self._image_base_url}{logo_path}" if logo_path is not None else None
                        ),
                    )
                )
        return tuple(providers)
