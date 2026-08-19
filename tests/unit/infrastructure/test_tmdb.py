from datetime import date

from reelore.application.availability import AvailabilityType
from reelore.application.catalog import TVEpisodeMetadata, TVSeriesCatalog
from reelore.infrastructure.tmdb import TMDBItalianLocalizer
from reelore.infrastructure.tmdb_availability import TMDBItalianAvailabilityProvider


class StubAuthorizedJsonHttpClient:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, str]] = []

    def get(self, url: str, token: str) -> object:
        self.requests.append((url, token))
        return self.responses[url]


def test_tmdb_localizes_series_and_episode_metadata_in_italian() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?query=Severance&language=it-IT&include_adult=false"
    )
    details_url = "https://api.themoviedb.org/3/tv/95396?language=it-IT"
    season_url = "https://api.themoviedb.org/3/tv/95396/season/1?language=it-IT"
    client = StubAuthorizedJsonHttpClient(
        {
            search_url: {
                "results": [
                    {
                        "id": 95396,
                        "name": "Scissione",
                        "first_air_date": "2022-02-18",
                    }
                ]
            },
            details_url: {
                "id": 95396,
                "name": "Scissione",
                "overview": "I dipendenti separano i ricordi del lavoro da quelli privati.",
            },
            season_url: {
                "episodes": [
                    {
                        "episode_number": 1,
                        "name": "Buone notizie sull'inferno",
                        "overview": "Mark torna al lavoro.",
                    }
                ]
            },
        }
    )
    catalog = TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary="English summary",
        status="Running",
        premiered=date(2022, 2, 18),
        ended=None,
        image_url=None,
        episodes=(
            TVEpisodeMetadata(
                provider_id="2001",
                season_number=1,
                episode_number=1,
                title="Good News About Hell",
            ),
        ),
    )

    localized = TMDBItalianLocalizer("secret-token", client).localize(catalog)

    assert localized is not None
    assert localized.title == "Scissione"
    assert localized.summary == "I dipendenti separano i ricordi del lavoro da quelli privati."
    assert localized.episodes[0].title == "Buone notizie sull'inferno"
    assert localized.episodes[0].summary == "Mark torna al lavoro."
    assert all(token == "secret-token" for _, token in client.requests)


def test_tmdb_returns_none_when_no_series_matches() -> None:
    url = "https://api.themoviedb.org/3/search/tv?query=Unknown&language=it-IT&include_adult=false"
    client = StubAuthorizedJsonHttpClient({url: {"results": []}})
    catalog = TVSeriesCatalog(
        provider_id="1",
        title="Unknown",
        summary=None,
        status=None,
        premiered=None,
        ended=None,
        image_url=None,
    )

    assert TMDBItalianLocalizer("secret-token", client).localize(catalog) is None


def test_tmdb_maps_italian_season_watch_providers_with_justwatch_attribution() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?query=Severance&language=it-IT&include_adult=false"
    )
    providers_url = "https://api.themoviedb.org/3/tv/95396/season/2/watch/providers"
    client = StubAuthorizedJsonHttpClient(
        {
            search_url: {
                "results": [
                    {
                        "id": 95396,
                        "first_air_date": "2022-02-18",
                    }
                ]
            },
            providers_url: {
                "results": {
                    "IT": {
                        "link": "https://www.themoviedb.org/tv/95396/watch?locale=IT",
                        "flatrate": [
                            {
                                "provider_name": "Apple TV Plus",
                                "logo_path": "/apple.jpg",
                            }
                        ],
                        "buy": [
                            {
                                "provider_name": "Example Store",
                                "logo_path": None,
                            }
                        ],
                    }
                }
            },
        }
    )
    catalog = TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary=None,
        status="Running",
        premiered=date(2022, 2, 18),
        ended=None,
        image_url=None,
    )

    availability = TMDBItalianAvailabilityProvider("secret-token", client).season_availability(
        catalog,
        2,
        "IT",
    )

    assert availability is not None
    assert availability.region == "IT"
    assert availability.season_number == 2
    assert availability.source == "JustWatch"
    assert availability.source_url == "https://www.themoviedb.org/tv/95396/watch?locale=IT"
    assert availability.providers[0].name == "Apple TV Plus"
    assert availability.providers[0].availability_type is AvailabilityType.STREAM
    assert availability.providers[0].logo_url == "https://image.tmdb.org/t/p/w92/apple.jpg"
    assert availability.providers[1].availability_type is AvailabilityType.BUY


def test_tmdb_falls_back_to_series_watch_providers_for_future_season() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?query=Ted+Lasso&language=it-IT&include_adult=false"
    )
    season_url = "https://api.themoviedb.org/3/tv/97546/season/4/watch/providers"
    series_url = "https://api.themoviedb.org/3/tv/97546/watch/providers"
    client = StubAuthorizedJsonHttpClient(
        {
            search_url: {"results": [{"id": 97546, "first_air_date": "2020-08-14"}]},
            season_url: {"results": {}},
            series_url: {
                "results": {
                    "IT": {
                        "link": "https://www.themoviedb.org/tv/97546/watch?locale=IT",
                        "flatrate": [
                            {
                                "provider_name": "Apple TV Plus",
                                "logo_path": "/apple.jpg",
                            }
                        ],
                    }
                }
            },
        }
    )
    catalog = TVSeriesCatalog(
        provider_id="52",
        title="Ted Lasso",
        summary=None,
        status="Running",
        premiered=date(2020, 8, 14),
        ended=None,
        image_url=None,
    )

    availability = TMDBItalianAvailabilityProvider("secret-token", client).season_availability(
        catalog,
        4,
        "IT",
    )

    assert availability is not None
    assert availability.season_number == 4
    assert availability.providers[0].name == "Apple TV Plus"
    assert availability.providers[0].availability_type is AvailabilityType.STREAM


def test_tmdb_returns_no_availability_when_region_is_missing() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?query=Severance&language=it-IT&include_adult=false"
    )
    season_url = "https://api.themoviedb.org/3/tv/95396/season/1/watch/providers"
    series_url = "https://api.themoviedb.org/3/tv/95396/watch/providers"
    client = StubAuthorizedJsonHttpClient(
        {
            search_url: {"results": [{"id": 95396}]},
            season_url: {"results": {"US": {"flatrate": []}}},
            series_url: {"results": {"US": {"flatrate": []}}},
        }
    )
    catalog = TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary=None,
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
    )

    availability = TMDBItalianAvailabilityProvider("secret-token", client).season_availability(
        catalog,
        1,
        "IT",
    )

    assert availability is None
