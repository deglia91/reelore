from fastapi import FastAPI
from fastapi.testclient import TestClient

from reelore.application.library_view import LibraryItemView, TopTenItemView
from reelore.domain import LibraryStatus
from reelore.web_top_ten import install_top_ten_routes, render_top_ten_page


def _library_item(
    media_id: str,
    title: str,
    status: LibraryStatus,
    image_url: str | None,
    *,
    top_ten_rank: int | None = None,
) -> LibraryItemView:
    return LibraryItemView(
        media_id=media_id,
        title=title,
        status=status,
        completion_count=0,
        rewatch_count=0,
        image_url=image_url,
        seen_episodes=0,
        total_episodes=0,
        top_ten_rank=top_ten_rank,
    )


class StubViews:
    def list_top_ten(self) -> tuple[TopTenItemView, ...]:
        return ()

    def list_items(self) -> tuple[LibraryItemView, ...]:
        return (_library_item("tvmaze:1", "The Bear", LibraryStatus.IN_PROGRESS, None),)


class StubTopTen:
    def __init__(self) -> None:
        self.assigned: list[tuple[str, int]] = []
        self.removed: list[str] = []

    def assign(self, media_id: str, rank: int) -> object:
        self.assigned.append((media_id, rank))
        return object()

    def remove(self, media_id: str) -> object:
        self.removed.append(media_id)
        return object()


def test_top_ten_page_renders_all_ten_positions_and_empty_slots() -> None:
    ranked = (
        TopTenItemView(
            rank=2,
            media_id="tvmaze:1",
            title="The Bear",
            image_url="https://img.example/the-bear.jpg",
        ),
    )
    library = (
        _library_item(
            "tvmaze:1",
            "The Bear",
            LibraryStatus.IN_PROGRESS,
            "https://img.example/the-bear.jpg",
            top_ten_rank=2,
        ),
    )

    page = render_top_ten_page(ranked, library)

    for rank in range(1, 11):
        assert f'data-rank="{rank}"' in page
    assert "The Bear" in page
    assert "In corso" in page
    assert page.count("Posizione libera") == 9


def test_top_ten_page_links_ranked_series_to_detail() -> None:
    ranked = (
        TopTenItemView(
            rank=1,
            media_id="tvmaze:42",
            title="Severance",
            image_url=None,
        ),
    )
    library = (
        _library_item(
            "tvmaze:42",
            "Severance",
            LibraryStatus.UP_TO_DATE,
            None,
            top_ten_rank=1,
        ),
    )

    page = render_top_ten_page(ranked, library)

    assert 'href="/series/tvmaze:42"' in page
    assert "In pari" in page


def test_top_ten_page_exposes_ranked_positions_in_management_selects() -> None:
    ranked = (TopTenItemView(2, "tvmaze:1", "The Bear", None),)
    library = (
        _library_item(
            "tvmaze:1",
            "The Bear",
            LibraryStatus.IN_PROGRESS,
            None,
            top_ten_rank=2,
        ),
        _library_item("tvmaze:2", "Severance", LibraryStatus.UP_TO_DATE, None),
    )

    page = render_top_ten_page(ranked, library)

    assert "The Bear (#2)" in page
    assert 'class="top-ten-management" method="post" action="/top-ten/2"' in page
    assert 'name="media_id"' in page
    assert 'action="/top-ten/tvmaze:1/remove"' in page


def test_top_ten_routes_assign_and_remove_from_dedicated_page() -> None:
    app = FastAPI()
    top_ten = StubTopTen()
    install_top_ten_routes(app, StubViews(), top_ten)
    client = TestClient(app)

    assigned = client.post(
        "/top-ten/3",
        data={"media_id": "tvmaze:1"},
        follow_redirects=False,
    )
    removed = client.post("/top-ten/tvmaze:1/remove", follow_redirects=False)

    assert assigned.status_code == 303
    assert assigned.headers["location"] == "/top-ten"
    assert top_ten.assigned == [("tvmaze:1", 3)]
    assert removed.status_code == 303
    assert removed.headers["location"] == "/top-ten"
    assert top_ten.removed == ["tvmaze:1"]
