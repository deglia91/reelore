from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import COMPONENT_CSS


def test_mobile_home_hides_redundant_intro_block() -> None:
    assert ".home-page .home-hero" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS


def test_mobile_home_search_starts_close_to_header() -> None:
    assert ".home-page main" in NAVIGATION_CSS
    assert "padding-top: var(--space-4)" in NAVIGATION_CSS
    assert ".home-page .search" in NAVIGATION_CSS
    assert "margin: 0 0 var(--space-4)" in NAVIGATION_CSS


def test_mobile_series_detail_expands_secondary_content_below_poster() -> None:
    assert ".detail-page .series-hero-content" in NAVIGATION_CSS
    assert "display: contents" in NAVIGATION_CSS
    assert ".detail-page .series-hero .summary" in NAVIGATION_CSS
    assert ".detail-page .series-hero .tracking-panel" in NAVIGATION_CSS
    assert ".detail-page .series-hero-content > .status-form" in NAVIGATION_CSS
    assert "grid-column: 1 / -1" in NAVIGATION_CSS


def test_mobile_season_actions_use_a_compact_two_column_grid() -> None:
    assert ".season-actions" in COMPONENT_CSS
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in COMPONENT_CSS
    assert ".season-actions .season-progress" in COMPONENT_CSS
    assert ".season-actions .season-complete" in COMPONENT_CSS
    assert "grid-column: 1 / -1" in COMPONENT_CSS
    assert ".season-actions button" in COMPONENT_CSS
    assert "width: 100%" in COMPONENT_CSS
