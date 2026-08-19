from reelore.web_theme import COMPONENT_CSS


def test_mobile_navigation_respects_browser_safe_area_and_stays_compact() -> None:
    assert "env(safe-area-inset-bottom)" in COMPONENT_CSS
    assert "--mobile-nav-height" in COMPONENT_CSS
    assert ".mobile-nav" in COMPONENT_CSS


def test_mobile_series_detail_uses_compact_episode_actions() -> None:
    assert ".episode button" in COMPONENT_CSS
    assert "width: auto" in COMPONENT_CSS
    assert "min-width: 92px" in COMPONENT_CSS


def test_mobile_home_reduces_intro_vertical_space() -> None:
    assert ".home-page .home-hero" in COMPONENT_CSS
    assert "margin-bottom: 0" in COMPONENT_CSS
