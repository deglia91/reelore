from reelore.domain import LibraryStatus
from reelore.web import _render_library_filters


def test_library_filters_include_dropped_status() -> None:
    filters = _render_library_filters(None)

    assert 'href="/library?status=dropped">Non più seguita</a>' in filters


def test_library_filters_mark_dropped_status_as_active() -> None:
    filters = _render_library_filters(LibraryStatus.DROPPED)

    assert 'class="filter-chip active" href="/library?status=dropped"' in filters
