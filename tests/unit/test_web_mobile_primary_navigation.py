from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_primary_navigation_keeps_history_and_top_ten_visible_as_icons() -> None:
    assert "--next-ep-history-icon" in NAVIGATION_CSS
    assert "--next-ep-top-ten-icon" in NAVIGATION_CSS
    assert 'a[href="/history"]::before' in NAVIGATION_CSS
    assert 'a[href="/top-ten"]::before' in NAVIGATION_CSS


def test_mobile_primary_navigation_compacts_brand_on_narrow_screens() -> None:
    assert "@media (max-width: 420px)" in NAVIGATION_CSS
    assert ".app-header .brand::after" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS


def test_primary_navigation_exposes_current_and_keyboard_focus_states() -> None:
    assert '.library-page .desktop-nav a[href="/library"]' in NAVIGATION_CSS
    assert '.calendar-page .desktop-nav a[href="/calendar"]' in NAVIGATION_CSS
    assert ".desktop-nav a:focus-visible" in NAVIGATION_CSS
    assert ".filter-chip:focus-visible" in NAVIGATION_CSS
