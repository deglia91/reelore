from reelore.web import _render_app_header, _render_mobile_nav


def test_global_navigation_links_to_watch_history() -> None:
    desktop = _render_app_header()
    mobile = _render_mobile_nav()

    assert '<a href="/history">Cronologia</a>' in desktop
    assert '<a href="/history">Cronologia</a>' in mobile
