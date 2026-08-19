from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_hero_hides_redundant_title_and_subtitle() -> None:
    assert ".home-page .home-hero h1" in NAVIGATION_CSS
    assert ".home-page .home-hero .sub" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS


def test_mobile_hero_keeps_personal_collection_eyebrow_compact() -> None:
    assert ".home-page .home-hero .eyebrow" in NAVIGATION_CSS
    assert "margin-bottom: 0" in NAVIGATION_CSS
    assert "padding-top: var(--space-2)" in NAVIGATION_CSS
