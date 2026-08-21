from reelore.web import _render_mobile_nav
from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_header_hides_primary_navigation_actions() -> None:
    assert "@media (max-width: 720px)" in NAVIGATION_CSS
    assert ".app-header .desktop-nav" in NAVIGATION_CSS
    assert "display: none !important" in NAVIGATION_CSS


def test_mobile_bottom_navigation_exposes_five_primary_destinations() -> None:
    navigation = _render_mobile_nav()

    for href, label in (
        ('href="/"', "Home"),
        ('href="/library"', "Libreria"),
        ('href="/calendar"', "Calendario"),
        ('href="/top-ten"', "Top 10"),
        ('href="/#search"', "Cerca"),
    ):
        assert href in navigation
        assert label in navigation
    assert 'href="/history"' not in navigation


def test_mobile_bottom_navigation_is_fixed_and_preserves_content_space() -> None:
    assert "position: fixed" in NAVIGATION_CSS
    assert "safe-area-inset-bottom" in NAVIGATION_CSS
    assert "padding-bottom: calc(" in NAVIGATION_CSS


def test_primary_navigation_exposes_current_and_keyboard_focus_states() -> None:
    assert '.library-page .desktop-nav a[href="/library"]' in NAVIGATION_CSS
    assert '.calendar-page .desktop-nav a[href="/calendar"]' in NAVIGATION_CSS
    assert ".desktop-nav a:focus-visible" in NAVIGATION_CSS
    assert ".filter-chip:focus-visible" in NAVIGATION_CSS
