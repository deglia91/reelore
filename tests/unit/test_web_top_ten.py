from reelore.application.library_view import TopTenItemView
from reelore.domain import LibraryStatus
from reelore.web_top_ten import render_top_ten_page


def test_top_ten_page_renders_all_ten_positions_and_empty_slots() -> None:
    page = render_top_ten_page(
        (
            TopTenItemView(
                rank=2,
                media_id="tvmaze:1",
                title="The Bear",
                image_url="https://img.example/the-bear.jpg",
                status=LibraryStatus.IN_PROGRESS,
            ),
        )
    )

    for rank in range(1, 11):
        assert f'data-rank="{rank}"' in page
    assert "The Bear" in page
    assert "In corso" in page
    assert page.count("Posizione libera") == 9


def test_top_ten_page_links_ranked_series_to_detail() -> None:
    page = render_top_ten_page(
        (
            TopTenItemView(
                rank=1,
                media_id="tvmaze:42",
                title="Severance",
                image_url=None,
                status=LibraryStatus.UP_TO_DATE,
            ),
        )
    )

    assert 'href="/series/tvmaze:42"' in page
    assert "In pari" in page
