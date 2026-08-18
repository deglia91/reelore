from reelore.web_theme import COMPONENT_CSS


def test_shared_controls_have_focus_and_secondary_button_states() -> None:
    assert ":focus-visible" in COMPONENT_CSS
    assert ".button-secondary" in COMPONENT_CSS
    assert "--color-accent" in COMPONENT_CSS


def test_cards_and_detail_controls_share_motion_and_surface_language() -> None:
    assert ".card:hover" in COMPONENT_CSS
    assert ".tracking-panel > div" in COMPONENT_CSS
    assert "var(--motion-base)" in COMPONENT_CSS


def test_mobile_polish_keeps_touch_targets_comfortable() -> None:
    assert "min-height: 44px" in COMPONENT_CSS
    assert ".mobile-nav a" in COMPONENT_CSS
