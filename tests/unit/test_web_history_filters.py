from datetime import datetime

from reelore.application.watch_history_view import WatchHistoryItemView
from reelore.web_history import render_history_page


def _entry(*, media_id: str, title: str, watch_number: int) -> WatchHistoryItemView:
    return WatchHistoryItemView(
        media_id=media_id,
        series_title=title,
        season_number=1,
        episode_number=1,
        episode_title="Pilot",
        watched_at=datetime(2026, 8, 21, 20, 0),
        watch_number=watch_number,
    )


def test_history_filters_rewatches_without_losing_filter_navigation() -> None:
    page = render_history_page(
        (
            _entry(media_id="tvmaze:1", title="First Watch", watch_number=1),
            _entry(media_id="tvmaze:2", title="Rewatch", watch_number=2),
        ),
        selected_filter="rewatch",
    )

    assert "First Watch" not in page
    assert "Rewatch" in page
    assert 'href="/history">Tutte</a>' in page
    assert 'href="/history?filter=first">Prime visioni</a>' in page
    assert 'class="filter-chip active" href="/history?filter=rewatch"' in page


def test_history_filters_first_watches() -> None:
    page = render_history_page(
        (
            _entry(media_id="tvmaze:1", title="First Watch", watch_number=1),
            _entry(media_id="tvmaze:2", title="Rewatch", watch_number=2),
        ),
        selected_filter="first",
    )

    assert "First Watch" in page
    assert "Rewatch" not in page
