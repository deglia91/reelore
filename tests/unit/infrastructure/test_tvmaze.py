from datetime import date

import pytest

from reelore.infrastructure import TVMazeProvider


class StubJsonHttpClient:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requested_urls: list[str] = []

    def get(self, url: str) -> object:
        self.requested_urls.append(url)
        return self.responses[url]


def test_tvmaze_search_maps_provider_neutral_results() -> None:
    url = "https://api.tvmaze.com/search/shows?q=Severance"
    client = StubJsonHttpClient(
        {
            url: [
                {
                    "show": {
                        "id": 16740,
                        "name": "Severance",
                        "premiered": "2022-02-18",
                        "status": "Running",
                        "image": {"original": "https://img.example/severance.jpg"},
                    }
                }
            ]
        }
    )

    results = TVMazeProvider(client).search(" Severance ")

    assert results[0].provider_id == "16740"
    assert results[0].title == "Severance"
    assert results[0].premiered == date(2022, 2, 18)
    assert results[0].image_url == "https://img.example/severance.jpg"
    assert client.requested_urls == [url]


def test_tvmaze_search_rejects_empty_query() -> None:
    with pytest.raises(ValueError, match="search query"):
        TVMazeProvider(StubJsonHttpClient({})).search("   ")


def test_tvmaze_series_maps_numbered_episodes_and_cast() -> None:
    url = "https://api.tvmaze.com/shows/16740?embed%5B%5D=episodes&embed%5B%5D=cast"
    client = StubJsonHttpClient(
        {
            url: {
                "id": 16740,
                "name": "Severance",
                "summary": "Office workers undergo a severance procedure.",
                "status": "Running",
                "premiered": "2022-02-18",
                "ended": None,
                "image": {"original": "https://img.example/show.jpg"},
                "_embedded": {
                    "episodes": [
                        {
                            "id": 2001,
                            "season": 1,
                            "number": 1,
                            "name": "Good News About Hell",
                            "airdate": "2022-02-18",
                            "summary": "Mark returns to work.",
                            "image": {"original": "https://img.example/e1.jpg"},
                            "runtime": 57,
                        },
                        {
                            "id": 2999,
                            "season": 0,
                            "number": None,
                            "name": "Special",
                        },
                    ],
                    "cast": [
                        {
                            "person": {
                                "name": "Adam Scott",
                                "image": {"medium": "https://img.example/adam.jpg"},
                            },
                            "character": {"name": "Mark Scout"},
                        }
                    ],
                },
            }
        }
    )

    series = TVMazeProvider(client).get_series("16740")

    assert series.title == "Severance"
    assert series.episodes[0].season_number == 1
    assert series.episodes[0].episode_number == 1
    assert series.episodes[0].runtime_minutes == 57
    assert len(series.episodes) == 1
    assert series.cast[0].person_name == "Adam Scott"
    assert series.cast[0].character_name == "Mark Scout"
