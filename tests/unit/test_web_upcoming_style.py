from reelore.web_theme import COMPONENT_CSS, render_theme_css


def test_upcoming_releases_use_vertical_dynamic_layout() -> None:
    assert "#upcoming .grid" in COMPONENT_CSS
    assert "grid-template-columns: 1fr" in COMPONENT_CSS
    assert "#upcoming .card" in COMPONENT_CSS
    assert "grid-template-columns: 112px minmax(0, 1fr)" in COMPONENT_CSS
    assert "#upcoming .meta" in COMPONENT_CSS


def test_home_upcoming_keeps_only_primary_platform_logo() -> None:
    assert ".home-page #upcoming .upcoming-platform:not(:first-child)" in COMPONENT_CSS
    assert ".home-page #upcoming .upcoming-platform > span" in COMPONENT_CSS
    assert "display: none" in COMPONENT_CSS


def test_dynamic_components_are_in_rendered_theme() -> None:
    assert COMPONENT_CSS in render_theme_css()
