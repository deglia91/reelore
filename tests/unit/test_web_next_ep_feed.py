from reelore.web import _render_home
from reelore.web_navigation_theme import NAVIGATION_CSS


def test_home_keeps_upcoming_and_top_ten_sections_visible_when_empty() -> None:
    page = _render_home("", (), (), (), ())

    assert 'id="upcoming"' in page
    assert "Nessuna nuova uscita in programma" in page
    assert 'id="top-ten"' in page
    assert "Nessuna serie nella Top 10" in page


def test_mobile_upcoming_is_visible_compact_episode_list() -> None:
    assert ".home-page #upcoming" in NAVIGATION_CSS
    assert "display: block !important" in NAVIGATION_CSS
    assert ".home-page #upcoming .grid" in NAVIGATION_CSS
    assert "grid-template-columns: 1fr" in NAVIGATION_CSS
    assert ".home-page #upcoming .card" in NAVIGATION_CSS
    assert "grid-template-columns: 68px minmax(0, 1fr)" in NAVIGATION_CSS


def test_mobile_continue_watching_matches_compact_library_cards() -> None:
    assert '#library .home-rail .card:has(.quick-action)' in NAVIGATION_CSS
    assert "flex: 0 0 40vw" in NAVIGATION_CSS
    assert "display: block" in NAVIGATION_CSS
    assert "aspect-ratio: 2 / 3" in NAVIGATION_CSS
    assert "min-height: 44px" in NAVIGATION_CSS


def test_mobile_top_ten_is_visible_compact_poster_rail() -> None:
    assert ".home-page #top-ten" in NAVIGATION_CSS
    assert "display: block !important" in NAVIGATION_CSS
    assert ".home-page #top-ten .grid" in NAVIGATION_CSS
    assert "overflow-x: auto" in NAVIGATION_CSS
    assert ".home-page #top-ten .top-ten-card" in NAVIGATION_CSS
    assert "flex: 0 0 118px" in NAVIGATION_CSS
