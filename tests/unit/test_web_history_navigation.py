from reelore.web import _render_app_header, _render_mobile_nav
from reelore.web_history import render_history_page


def test_global_navigation_links_to_watch_history() -> None:
    desktop = _render_app_header()
    mobile = _render_mobile_nav()

    assert '<a href="/history">Cronologia</a>' in desktop
    assert '<a href="/history">Cronologia</a>' in mobile


def test_global_navigation_links_to_dedicated_top_ten_page() -> None:
    desktop = _render_app_header()
    mobile = _render_mobile_nav()
    history = render_history_page(())

    assert '<a href="/top-ten">Top 10</a>' in desktop
    assert '<a href="/top-ten">Top 10</a>' in mobile
    assert history.count('href="/top-ten">Top 10</a>') == 2
