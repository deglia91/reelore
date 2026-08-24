from reelore.application import WatchStatistics
from reelore.web_stats import format_watch_time, render_statistics_page


def test_format_watch_time_uses_days_hours_and_minutes() -> None:
    assert format_watch_time(3_125) == "2 giorni 4 ore 5 min"
    assert format_watch_time(125) == "2 ore 5 min"
    assert format_watch_time(45) == "45 min"


def test_statistics_page_renders_watch_activity_summary() -> None:
    page = render_statistics_page(
        WatchStatistics(
            total_watch_minutes=3_125,
            total_watches=75,
            unique_episodes=70,
            rewatches=5,
        )
    )

    assert "Statistiche" in page
    assert "Tempo totale visto" in page
    assert "2 giorni 4 ore 5 min" in page
    assert "52 ore totali" in page
    assert "75" in page
    assert "70" in page
    assert "5" in page
    assert 'href="/history"' in page
