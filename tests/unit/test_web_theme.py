from reelore.web_theme import FOUNDATION_CSS, REEL_ORE_SKIN_CSS, render_theme_css


def test_foundation_defines_structural_tokens_without_brand_colors() -> None:
    assert "--space-4" in FOUNDATION_CSS
    assert "--radius-md" in FOUNDATION_CSS
    assert "--motion-base" in FOUNDATION_CSS
    assert "--color-accent" not in FOUNDATION_CSS


def test_skin_owns_semantic_colors() -> None:
    assert "--color-bg" in REEL_ORE_SKIN_CSS
    assert "--color-surface" in REEL_ORE_SKIN_CSS
    assert "--color-accent" in REEL_ORE_SKIN_CSS
    assert "--color-success" in REEL_ORE_SKIN_CSS


def test_rendered_theme_combines_foundation_and_skin() -> None:
    rendered = render_theme_css()

    assert FOUNDATION_CSS in rendered
    assert REEL_ORE_SKIN_CSS in rendered
