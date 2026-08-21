from reelore.web import _render_app_header
from reelore.web_navigation_theme import NAVIGATION_CSS


def test_header_uses_minimal_tech_wordmark_structure() -> None:
    header = _render_app_header()

    assert 'class="brand-word"' in header
    assert 'class="brand-accent">Ep</span>' in header
    assert 'data-icon="next-episode"' in header


def test_header_uses_one_coherent_icon_family_for_primary_navigation() -> None:
    header = _render_app_header()

    for icon in ("library", "calendar", "history", "top-ten", "search"):
        assert f'data-icon="{icon}"' in header


def test_mobile_navigation_keeps_matching_minimal_tech_masks() -> None:
    for token in (
        "--next-ep-logo-icon",
        "--next-ep-library-icon",
        "--next-ep-calendar-icon",
        "--next-ep-history-icon",
        "--next-ep-top-ten-icon",
        "--next-ep-search-icon",
    ):
        assert token in NAVIGATION_CSS
    assert "stroke-linecap=%27round%27" in NAVIGATION_CSS
