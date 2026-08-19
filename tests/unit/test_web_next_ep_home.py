from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_shell_moves_primary_actions_to_header() -> None:
    assert ".app-header .desktop-nav" in NAVIGATION_CSS
    assert 'a[href="/calendar"]' in NAVIGATION_CSS
    assert 'a[href="/library"]' in NAVIGATION_CSS
    assert 'a[href="/#search"]' in NAVIGATION_CSS
    assert "body .mobile-nav" in NAVIGATION_CSS
    assert "display: none !important" in NAVIGATION_CSS


def test_mobile_shell_uses_safari_safe_vector_icons() -> None:
    assert "--next-ep-logo-icon" in NAVIGATION_CSS
    assert "--next-ep-calendar-icon" in NAVIGATION_CSS
    assert "--next-ep-library-icon" in NAVIGATION_CSS
    assert "--next-ep-search-icon" in NAVIGATION_CSS
    assert "background-image: var(--next-ep-logo-icon)" in NAVIGATION_CSS
    assert "background-image: var(--next-ep-calendar-icon)" in NAVIGATION_CSS
    assert "background-image: var(--next-ep-library-icon)" in NAVIGATION_CSS
    assert "background-image: var(--next-ep-search-icon)" in NAVIGATION_CSS
    assert "mask-image:" not in NAVIGATION_CSS
    assert "-webkit-mask-image:" not in NAVIGATION_CSS


def test_mobile_search_is_compact_single_row_with_icon_button() -> None:
    assert ".home-page .search" in NAVIGATION_CSS
    assert "flex-direction: row" in NAVIGATION_CSS
    assert ".home-page .search button" in NAVIGATION_CSS
    assert ".home-page .search button::before" in NAVIGATION_CSS
    assert "background-image: var(--next-ep-search-icon)" in NAVIGATION_CSS


def test_mobile_home_prioritizes_continue_watching_after_search() -> None:
    assert ".home-page #library" in NAVIGATION_CSS
    assert "order: 4" in NAVIGATION_CSS
    assert ".home-page #library > section:not(:first-child)" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS
    assert ".home-page #upcoming" in NAVIGATION_CSS
    assert "order: 5" in NAVIGATION_CSS
    assert ".home-page #top-ten" in NAVIGATION_CSS
    assert "order: 6" in NAVIGATION_CSS


def test_mobile_home_removes_redundant_intro_and_large_vertical_gap() -> None:
    assert ".home-page .home-hero" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS
    assert ".home-page .search + #library" not in NAVIGATION_CSS
    assert "margin-top: var(--space-4)" in NAVIGATION_CSS
