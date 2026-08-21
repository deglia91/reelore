from reelore.web import _render_app_header
from reelore.web_navigation_theme import NAVIGATION_CSS


def test_header_keeps_semantic_next_ep_brand_anchor() -> None:
    header = _render_app_header()

    assert 'aria-label="NextEp Home"' in header
    assert 'data-icon="next-episode"' in header
    assert "NextEp" in header


def test_navigation_theme_defines_minimal_tech_brand_treatment() -> None:
    assert ".app-header .brand-mark" in NAVIGATION_CSS
    assert "linear-gradient(135deg" in NAVIGATION_CSS
    assert "filter: drop-shadow" in NAVIGATION_CSS
    assert ".app-header .brand" in NAVIGATION_CSS


def test_primary_navigation_uses_one_coherent_minimal_tech_icon_family() -> None:
    for token in (
        "--next-ep-logo-icon",
        "--next-ep-library-icon",
        "--next-ep-calendar-icon",
        "--next-ep-history-icon",
        "--next-ep-top-ten-icon",
        "--next-ep-search-icon",
    ):
        assert token in NAVIGATION_CSS
    for href in ("/library", "/calendar", "/history", "/top-ten", "/#search"):
        assert f'a[href="{href}"]::before' in NAVIGATION_CSS
    assert "stroke-linecap=%27round%27" in NAVIGATION_CSS


def test_minimal_tech_masks_include_svg_namespace_for_safari() -> None:
    svg_count = NAVIGATION_CSS.count("data:image/svg+xml")
    namespace_count = NAVIGATION_CSS.count("xmlns=%27http://www.w3.org/2000/svg%27")

    assert svg_count > 0
    assert namespace_count == svg_count


def test_minimal_tech_logo_uses_bolder_double_forward_geometry() -> None:
    assert "stroke-width=%272.2%27" in NAVIGATION_CSS
    assert "M3.5%205L11%2012l-7.5%207" in NAVIGATION_CSS


def test_mobile_header_icons_do_not_use_permanent_boxes() -> None:
    assert "border: 1px solid transparent" in NAVIGATION_CSS
    assert "background: transparent" in NAVIGATION_CSS
    assert ".app-header .desktop-nav a:hover" in NAVIGATION_CSS
