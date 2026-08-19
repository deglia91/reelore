from reelore.web import _page, _render_home
from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_shell_moves_primary_actions_to_header() -> None:
    assert ".app-header .desktop-nav" in NAVIGATION_CSS
    assert 'a[href="/calendar"]' in NAVIGATION_CSS
    assert 'a[href="/library"]' in NAVIGATION_CSS
    assert 'a[href="/#search"]' in NAVIGATION_CSS
    assert "body .mobile-nav" in NAVIGATION_CSS
    assert "display: none !important" in NAVIGATION_CSS


def test_app_shell_renders_inline_next_ep_brand_and_navigation_icons() -> None:
    page = _page("<p>Content</p>", home=True)

    assert 'class="brand-icon"' in page
    assert 'data-icon="next-episode"' in page
    assert 'class="nav-icon"' in page
    assert 'data-icon="calendar"' in page
    assert 'data-icon="library"' in page
    assert 'data-icon="search"' in page
    assert "<svg" in page


def test_mobile_search_is_compact_single_row_with_inline_icon_button() -> None:
    page = _render_home("", (), (), (), ())

    assert ".home-page .search" in NAVIGATION_CSS
    assert "flex-direction: row" in NAVIGATION_CSS
    assert 'class="search-icon"' in page
    assert 'data-icon="search"' in page


def test_mobile_home_uses_natural_document_flow_after_search() -> None:
    assert ".home-page main" in NAVIGATION_CSS
    assert "display: block" in NAVIGATION_CSS
    assert ".home-page #library > section:not(:first-child)" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS
    assert ".home-page #upcoming" in NAVIGATION_CSS
    assert ".home-page #top-ten" in NAVIGATION_CSS
    assert "order: 5" not in NAVIGATION_CSS
    assert "order: 6" not in NAVIGATION_CSS


def test_mobile_home_removes_redundant_intro_and_large_vertical_gap() -> None:
    assert ".home-page .home-hero" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS
    assert ".home-page .search + #library" not in NAVIGATION_CSS
    assert "margin-top: var(--space-4)" in NAVIGATION_CSS
