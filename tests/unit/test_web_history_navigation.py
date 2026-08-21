from reelore.web import _render_app_header, _render_mobile_nav
from reelore.web_history import render_history_page
from reelore.web_navigation_theme import NAVIGATION_CSS


def test_global_navigation_links_to_watch_history() -> None:
    desktop = _render_app_header()
    mobile = _render_mobile_nav()

    assert '<a href="/history">Cronologia</a>' in desktop
    assert 'href="/history"' in mobile
    assert "Cronologia" in mobile


def test_global_navigation_links_to_dedicated_top_ten_page() -> None:
    desktop = _render_app_header()
    mobile = _render_mobile_nav()
    history = render_history_page(())

    assert '<a href="/top-ten">Top 10</a>' in desktop
    assert 'href="/top-ten"' in mobile
    assert "Top 10" in mobile
    assert 'href="/top-ten"' in history


def test_shared_mobile_navigation_marks_current_section() -> None:
    history = render_history_page(())

    assert 'href="/history" aria-current="page"' in history
    assert '.history-mobile-nav a[aria-current="page"]' in NAVIGATION_CSS
    assert '.history-mobile-nav a[href="/#search"]' in NAVIGATION_CSS
    assert "display: none !important" in NAVIGATION_CSS
