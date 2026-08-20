from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import COMPONENT_CSS


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
    assert "flex: 0 0 118px" in NAVIGATION_CSS
    assert "width: 118px" in NAVIGATION_CSS
    assert "font-size: .74rem" in NAVIGATION_CSS


def test_mobile_unseen_episode_actions_move_below_episode_copy() -> None:
    selector = '.episode:not(:has(.episode-actions form[action$="/rewatch"]))'
    assert selector in COMPONENT_CSS
    assert f"{selector} .episode-actions" in COMPONENT_CSS
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in COMPONENT_CSS
    assert f"{selector} .episode-actions form:only-child" in COMPONENT_CSS
