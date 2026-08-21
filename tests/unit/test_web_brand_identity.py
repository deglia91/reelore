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
        "--next-ep-brand-asset",
        "--next-ep-home-icon",
    ):
        assert token in NAVIGATION_CSS
    assert "stroke-linecap=%27round%27" in NAVIGATION_CSS


def test_minimal_tech_masks_include_svg_namespace_for_safari() -> None:
    svg_count = NAVIGATION_CSS.count("data:image/svg+xml")
    namespace_count = NAVIGATION_CSS.count("xmlns=%27http://www.w3.org/2000/svg%27")

    assert svg_count > 0
    assert namespace_count == svg_count


def test_shared_brand_uses_dedicated_logo_asset() -> None:
    assert "--next-ep-brand-asset" in NAVIGATION_CSS
    assert "background-image: var(--next-ep-brand-asset) !important" in NAVIGATION_CSS
    assert "mask-image: none !important" in NAVIGATION_CSS


def test_mobile_header_moves_actions_to_bottom_navigation() -> None:
    assert ".app-header .desktop-nav {\n    display: none !important;" in NAVIGATION_CSS
    assert "body .mobile-nav," in NAVIGATION_CSS
    assert "grid-template-columns: repeat(5, minmax(0, 1fr)) !important" in NAVIGATION_CSS
    assert 'body .mobile-nav a[href="/#search"]' in NAVIGATION_CSS
    assert 'body .mobile-nav a[href="/history"]::before' in NAVIGATION_CSS


def test_mobile_header_hides_legacy_brand_text() -> None:
    assert ".app-header .brand {" in NAVIGATION_CSS
    assert "font-size: 0 !important" in NAVIGATION_CSS


def test_mobile_home_tightens_search_to_continue_watching_gap() -> None:
    assert ".home-page #library > section:first-child" in NAVIGATION_CSS
    assert "margin-top: var(--space-2) !important" in NAVIGATION_CSS
