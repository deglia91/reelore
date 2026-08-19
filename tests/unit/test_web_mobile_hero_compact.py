from reelore.web_theme import COMPONENT_CSS


def test_mobile_hero_hides_redundant_title_and_subtitle() -> None:
    assert ".home-page .home-hero h1" in COMPONENT_CSS
    assert ".home-page .home-hero .sub" in COMPONENT_CSS
    assert "display: none" in COMPONENT_CSS


def test_mobile_hero_keeps_personal_collection_eyebrow_compact() -> None:
    assert ".home-page .home-hero .eyebrow" in COMPONENT_CSS
    assert "margin-bottom: 0" in COMPONENT_CSS
    assert "padding-top: var(--space-2)" in COMPONENT_CSS
