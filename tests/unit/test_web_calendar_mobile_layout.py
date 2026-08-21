from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_calendar_cards_keep_compact_layout_and_hide_source_noise() -> None:
    assert "@media (max-width: 720px)" in NAVIGATION_CSS
    assert ".calendar-entry {" in NAVIGATION_CSS
    assert "grid-template-columns: 68px minmax(0, 1fr);" in NAVIGATION_CSS
    assert ".calendar-entry-poster .poster," in NAVIGATION_CSS
    assert "width: 68px;" in NAVIGATION_CSS
    assert "height: 102px;" in NAVIGATION_CSS
    assert ".calendar-entry-copy {" in NAVIGATION_CSS
    assert "padding: var(--space-2) var(--space-3) var(--space-2) 0;" in NAVIGATION_CSS
    assert ".calendar-page .availability-source {" in NAVIGATION_CSS
    assert "display: none;" in NAVIGATION_CSS
