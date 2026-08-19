from reelore.web import _render_home
from reelore.web_theme import COMPONENT_CSS


def test_home_exposes_short_mobile_intro_copy() -> None:
    page = _render_home("", (), (), (), ())

    assert 'class="sub mobile-home-copy"' in page
    assert "Le storie che guardi, organizzate." in page


def test_mobile_hero_hides_redundant_title_and_desktop_copy() -> None:
    assert ".home-page .home-hero h1" in COMPONENT_CSS
    assert "display: none" in COMPONENT_CSS
    assert ".desktop-home-copy" in COMPONENT_CSS
    assert ".mobile-home-copy" in COMPONENT_CSS
