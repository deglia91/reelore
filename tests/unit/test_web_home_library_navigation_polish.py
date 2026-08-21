from reelore.domain import LibraryStatus
from reelore.web import _render_home, _render_library_filters


def test_home_uses_next_ep_product_name() -> None:
    page = _render_home("", (), (), (), (), ())

    assert '<h1 id="home-title">NextEp</h1>' in page


def test_home_top_ten_links_to_dedicated_page() -> None:
    page = _render_home("", (), (), (), (), ())

    assert '<a class="section-link" href="/top-ten">Vedi tutte</a>' in page


def test_active_library_filter_exposes_current_page_semantics() -> None:
    filters = _render_library_filters(LibraryStatus.IN_PROGRESS)

    assert 'class="filter-chip active" href="/library?status=in_progress" aria-current="page"' in filters
