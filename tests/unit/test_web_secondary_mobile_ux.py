from reelore.web_history import render_history_page
from reelore.web_top_ten import render_top_ten_page


def test_history_mobile_navigation_respects_safe_area() -> None:
    page = render_history_page(())

    assert "env(safe-area-inset-bottom)" in page
    assert "bottom: calc(12px + env(safe-area-inset-bottom))" in page


def test_top_ten_mobile_navigation_respects_safe_area() -> None:
    page = render_top_ten_page((), ())

    assert "env(safe-area-inset-bottom)" in page
    assert "bottom: calc(12px + env(safe-area-inset-bottom))" in page


def test_top_ten_mobile_management_controls_are_touch_sized() -> None:
    page = render_top_ten_page((), ())

    assert ".top-ten-management select" in page
    assert ".top-ten-management button" in page
    assert "min-height: 44px" in page
