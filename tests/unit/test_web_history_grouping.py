from datetime import datetime

from reelore.application.watch_history_view import WatchHistoryItemView
from reelore.web_history import render_history_page


def _entry(title: str, watched_at: datetime | None) -> WatchHistoryItemView:
    return WatchHistoryItemView(
        media_id=f"tvmaze:{title.lower()}",
        series_title=title,
        season_number=1,
        episode_number=1,
        episode_title="Pilot",
        watched_at=watched_at,
        watch_number=1,
    )


def test_history_groups_entries_under_day_headings() -> None:
    page = render_history_page(
        (
            _entry("Recent", datetime(2026, 8, 24, 21, 0)),
            _entry("Same Day", datetime(2026, 8, 24, 20, 0)),
            _entry("Previous", datetime(2026, 8, 23, 19, 0)),
        )
    )

    assert page.count('class="history-day"') == 2
    assert "24 ago 2026" in page
    assert "23 ago 2026" in page
    assert page.index("Recent") < page.index("Previous")


def test_history_keeps_legacy_entries_without_date_in_separate_group() -> None:
    page = render_history_page((_entry("Legacy", None),))

    assert "Data non disponibile" in page
    assert 'class="history-day"' in page
