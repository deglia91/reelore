from reelore.application.library_view import LibraryItemView, TopTenItemView
from reelore.domain import LibraryStatus
from reelore.web_top_ten import render_top_ten_page


def _library_item(
    media_id: str,
    title: str,
    status: LibraryStatus,
    image_url: str | None,
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
    )


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
        ),
    )

    page = render_top_ten_page(ranked, library)

    assert 'href="/series/tvmaze:42"' in page
    assert "In pari" in page
