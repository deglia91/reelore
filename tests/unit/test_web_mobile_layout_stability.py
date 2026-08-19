from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_document_cannot_pan_horizontally() -> None:
    assert "overflow-x: hidden" in NAVIGATION_CSS
    assert ".home-page main" in NAVIGATION_CSS
    assert "max-width: 100%" in NAVIGATION_CSS
    assert ".home-page main > *" in NAVIGATION_CSS
    assert "min-width: 0" in NAVIGATION_CSS


def test_home_rails_use_flex_scrolling_inside_the_viewport() -> None:
    assert ".home-rail" in NAVIGATION_CSS
    assert "display: flex" in NAVIGATION_CSS
    assert "overflow-x: auto" in NAVIGATION_CSS
    assert "-webkit-overflow-scrolling: touch" in NAVIGATION_CSS
    assert ".home-rail > *" in NAVIGATION_CSS
    assert "flex: 0 0 40vw" in NAVIGATION_CSS


def test_mobile_top_ten_is_a_compact_horizontal_rail() -> None:
    assert "#top-ten .grid" in NAVIGATION_CSS
    assert "display: flex" in NAVIGATION_CSS
    assert "flex: 0 0 34vw" in NAVIGATION_CSS
    assert "font-size: 1.5rem" in NAVIGATION_CSS
