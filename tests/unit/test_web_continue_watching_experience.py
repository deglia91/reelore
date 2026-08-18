from reelore.web_theme import COMPONENT_CSS


def test_continue_watching_uses_cinematic_layout_without_new_markup() -> None:
    assert "#library .card:has(.quick-action)" in COMPONENT_CSS
    assert "grid-template-columns: minmax(0, 1fr) auto" in COMPONENT_CSS
    assert "grid-template-columns: minmax(220px, 42%) minmax(0, 1fr)" in COMPONENT_CSS
    assert "box-shadow: var(--shadow-raised)" in COMPONENT_CSS


def test_continue_watching_collapses_for_mobile() -> None:
    assert "@media (max-width: 720px)" in COMPONENT_CSS
    assert "grid-template-columns: 118px minmax(0, 1fr)" in COMPONENT_CSS
    assert "width: 100%" in COMPONENT_CSS
