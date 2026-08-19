from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_home_contains_width_without_blocking_nested_scroll() -> None:
    assert "overflow-x: clip" not in NAVIGATION_CSS
    assert ".home-page main" in NAVIGATION_CSS
    assert "max-width: 100%" in NAVIGATION_CSS
    assert ".home-page main > *" in NAVIGATION_CSS
    assert "min-width: 0" in NAVIGATION_CSS
    assert ".home-page .home-hero" in NAVIGATION_CSS
    assert "overflow: hidden" in NAVIGATION_CSS


def test_home_rails_scroll_inside_the_viewport_on_touch_devices() -> None:
    assert ".home-rail" in NAVIGATION_CSS
    assert "width: 100%" in NAVIGATION_CSS
    assert "overflow-x: auto" in NAVIGATION_CSS
    assert "-webkit-overflow-scrolling: touch" in NAVIGATION_CSS
    assert "touch-action: pan-x" in NAVIGATION_CSS


def test_mobile_top_ten_is_a_compact_horizontal_rail() -> None:
    assert "#top-ten .grid" in NAVIGATION_CSS
    assert "display: flex" in NAVIGATION_CSS
    assert "flex: 0 0 46vw" in NAVIGATION_CSS
    assert "font-size: clamp(3rem, 13vw, 4.2rem)" in NAVIGATION_CSS
