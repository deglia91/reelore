from datetime import datetime

from reelore.application.watch_history_view import WatchHistoryItemView
from reelore.web_history import render_history_page


def test_history_page_renders_chronological_watch_entries() -> None:
    entries = (
        WatchHistoryItemView(
            media_id="tvmaze:1",
            series_title="Severance",
            season_number=1,
            episode_number=1,
            episode_title="Good News About Hell",
            watched_at=datetime(2026, 8, 20, 22, 15),
            watch_number=2,
        ),
        WatchHistoryItemView(
            media_id="tvmaze:2",
            series_title="The Bear",
            season_number=2,
            episode_number=3,
            episode_title="Sundae",
            watched_at=datetime(2026, 8, 19, 21, 0),
            watch_number=1,
        ),
    )

    page = render_history_page(entries)

    assert "Cronologia" in page
    assert 'href="/series/tvmaze:1"' in page
    assert "Severance" in page
    assert "S01E01" in page
    assert "Good News About Hell" in page
    assert "20 ago 2026 · 22:15" in page
    assert "2ª visione" in page
    assert "1ª visione" not in page


def test_history_page_preserves_legacy_watch_without_fake_date() -> None:
    page = render_history_page(
        (
            WatchHistoryItemView(
                media_id="tvmaze:1",
                series_title="Severance",
                season_number=1,
                episode_number=1,
                episode_title="Good News About Hell",
                watched_at=None,
                watch_number=1,
            ),
        )
    )

    assert "Data non disponibile" in page


def test_history_page_has_empty_state() -> None:
    page = render_history_page(())

    assert "Nessuna visione registrata" in page
