from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_home_hides_redundant_intro_block() -> None:
    assert ".home-page .home-hero" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS


def test_mobile_home_search_starts_close_to_header() -> None:
    assert ".home-page main" in NAVIGATION_CSS
    assert "padding-top: var(--space-4)" in NAVIGATION_CSS
    assert ".home-page .search" in NAVIGATION_CSS
    assert "margin: 0 0 var(--space-4)" in NAVIGATION_CSS
