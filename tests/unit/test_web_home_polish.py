from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import COMPONENT_CSS


def test_home_polish_defines_hero_search_and_section_hierarchy() -> None:
    assert ".home-page .home-hero" in COMPONENT_CSS
    assert ".home-page .home-hero::before" in COMPONENT_CSS
    assert ".home-page .search" in COMPONENT_CSS
    assert ".home-page .section-heading" in COMPONENT_CSS


def test_library_secondary_sections_are_visually_quieter() -> None:
    assert "#library > section:not(:first-child) .grid" in COMPONENT_CSS
    assert "#library > section:not(:first-child) .card" in COMPONENT_CSS
    assert "#library > section:not(:first-child) .meta" in COMPONENT_CSS


def test_recent_releases_use_a_compact_horizontal_rail() -> None:
    assert "#recent .grid" in NAVIGATION_CSS
    assert "overflow-x: auto" in NAVIGATION_CSS
    assert "#recent .card" in NAVIGATION_CSS
    assert "flex: 0 0 190px" in NAVIGATION_CSS


def test_home_polish_keeps_mobile_spacing_rules() -> None:
    assert "#library > section" in COMPONENT_CSS
    assert "margin-bottom: var(--space-6)" in COMPONENT_CSS
