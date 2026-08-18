from reelore.web_theme import COMPONENT_CSS


def test_top_ten_uses_cinematic_ranking_layout() -> None:
    assert "#top-ten .grid" in COMPONENT_CSS
    assert "#top-ten .top-ten-card" in COMPONENT_CSS
    assert "#top-ten .top-ten-rank" in COMPONENT_CSS
    assert "font-size: clamp(5.8rem, 9vw, 8rem)" in COMPONENT_CSS
    assert "text-shadow:" in COMPONENT_CSS
    assert "box-shadow: var(--shadow-raised)" in COMPONENT_CSS


def test_top_ten_has_mobile_ranking_layout() -> None:
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in COMPONENT_CSS
    assert "font-size: clamp(4.5rem, 22vw, 6.2rem)" in COMPONENT_CSS
