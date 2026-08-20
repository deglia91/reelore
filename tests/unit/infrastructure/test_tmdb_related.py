from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.infrastructure.tmdb_related import TMDBRelatedTVProvider


class StubAuthorizedJsonHttpClient:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, str]] = []

    def get(self, url: str, token: str) -> object:
        self.requests.append((url, token))
        return self.responses[url]


def test_tmdb_returns_italian_related_tv_titles() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?query=Loki&language=it-IT&include_adult=false"
    )
    related_url = (
        "https://api.themoviedb.org/3/tv/84958/recommendations?language=it-IT&page=1"
    )
    client = StubAuthorizedJsonHttpClient(
        {
            search_url: {
                "results": [
                    {
                        "id": 84958,
                        "first_air_date": "2021-06-09",
                    }
                ]
            },
            related_url: {
                "results": [
                    {
                        "id": 88396,
                        "name": "The Falcon and the Winter Soldier",
                        "overview": "Sam Wilson e Bucky Barnes affrontano una nuova minaccia.",
                        "first_air_date": "2021-03-19",
                        "poster_path": "/falcon.jpg",
                    },
                    {
                        "id": 92749,
                        "name": "Moon Knight",
                        "overview": "Steven Grant scopre un'altra identità.",
                        "first_air_date": "2022-03-30",
                        "poster_path": None,
                    },
                ]
            },
        }
    )
    catalog = TVSeriesCatalog(
        provider_id="41007",
        title="Loki",
        summary=None,
        status="Ended",
        premiered=date(2021, 6, 9),
        ended=None,
        image_url=None,
    )

    related = TMDBRelatedTVProvider("secret-token", client).related_to(catalog)

    assert related[0].provider_key == "88396"
    assert related[0].title == "The Falcon and the Winter Soldier"
    assert related[0].summary == "Sam Wilson e Bucky Barnes affrontano una nuova minaccia."
    assert related[0].premiered == date(2021, 3, 19)
    assert related[0].image_url == "https://image.tmdb.org/t/p/w342/falcon.jpg"
    assert related[1].provider_key == "92749"
    assert related[1].image_url is None
    assert all(token == "secret-token" for _, token in client.requests)


def test_tmdb_related_returns_empty_when_series_cannot_be_matched() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?query=Unknown&language=it-IT&include_adult=false"
    )
    client = StubAuthorizedJsonHttpClient({search_url: {"results": []}})
    catalog = TVSeriesCatalog(
        provider_id="1",
        title="Unknown",
        summary=None,
        status=None,
        premiered=None,
        ended=None,
        image_url=None,
    )

    assert TMDBRelatedTVProvider("secret-token", client).related_to(catalog) == ()


def test_tmdb_related_skips_entries_without_a_title() -> None:
    search_url = (
        "https://api.themoviedb.org/3/search/tv?query=Loki&language=it-IT&include_adult=false"
    )
    related_url = (
        "https://api.themoviedb.org/3/tv/84958/recommendations?language=it-IT&page=1"
    )
    client = StubAuthorizedJsonHttpClient(
        {
            search_url: {"results": [{"id": 84958}]},
            related_url: {
                "results": [
                    {"id": 1, "name": "", "overview": "Ignored"},
                    {"id": 2, "overview": "Also ignored"},
                ]
            },
        }
    )
    catalog = TVSeriesCatalog("41007", "Loki", None, None, None, None, None)

    assert TMDBRelatedTVProvider("secret-token", client).related_to(catalog) == ()
