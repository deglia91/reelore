from datetime import date

from reelore.application.catalog import TVEpisodeMetadata, TVSeriesCatalog
from reelore.infrastructure import TMDBItalianLocalizer


class StubAuthorizedJsonHttpClient:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, str]] = []

    def get(self, url: str, token: str) -> object:
        self.requests.append((url, token))
        return self.responses[url]


def test_tmdb_localizes_series_and_episode_metadata_in_italian() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?"
        "query=Severance&language=it-IT&include_adult=false"
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
    url = (
        "https://api.themoviedb.org/3/search/tv?"
        "query=Unknown&language=it-IT&include_adult=false"
    )
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
